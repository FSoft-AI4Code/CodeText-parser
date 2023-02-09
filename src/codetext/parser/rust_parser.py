import re
from typing import List, Dict, Any

import tree_sitter
import logging

from .language_parser import LanguageParser, get_node_by_kind, get_node_text


logger = logging.getLogger(__name__)


class RustParser(LanguageParser):

    FILTER_PATHS = ('test', 'vendor')

    BLACKLISTED_FUNCTION_NAMES = ['main']

    @staticmethod
    def get_function_list(node):
        res = get_node_by_kind(node, ['function_item'])
        return res
    
    @staticmethod
    def get_class_list(node):
        res = get_node_by_kind(node, ['impl_item', 'mod_item'])  # trait is like an interface
        return res

    @staticmethod
    def get_docstring_node(node) -> List:
        docstring_node = []
        
        prev_node = node.prev_sibling
        if prev_node:
            if prev_node.type == 'block_comment':
                docstring_node.append(prev_node)
                
            elif prev_node.type == 'line_comment':
                docstring_node.append(prev_node)
                prev_node = prev_node.prev_sibling
                
                while prev_node and prev_node.type == 'line_comment':
                    # Assume the comment is dense
                    x_current = prev_node.start_point[0]
                    x_next = prev_node.next_sibling.start_point[0]
                    if x_next - x_current > 1:
                        break
                            
                    docstring_node.insert(0, prev_node)    
                    prev_node = prev_node.prev_sibling
            
        return docstring_node
    
    @staticmethod
    def get_docstring(node, blob=None):
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        docstring_node = RustParser.get_docstring_node(node)
        docstring = []
        if docstring_node:
            for item in docstring_node:
                doc = get_node_text(item)
                docstring.append(doc)

        docstring = '\n'.join(docstring)
        return docstring
    
    @staticmethod
    def get_function_metadata(function_node, blob=None) -> Dict[str, str]:
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        metadata = {
            'identifier': '',
            'parameters': {},
            'return_type': None,
        }
        
        assert type(function_node) == tree_sitter.Node
        assert function_node.type == 'function_item'
        
        for child in function_node.children:
            if child.type == 'identifier':
                metadata['identifier'] = get_node_text(child)
            elif child.type in ['parameters']:
                params = get_node_by_kind(child, ['parameter', 'variadic_parameter', 'self_parameter'])
                for item in params:
                    if item.type == 'self_parameter':
                        metadata['parameters'][get_node_text(item)] = None
                    
                    else:
                        # param_name = ''
                        for subchild in item.children:
                            if subchild.type == 'identifier':
                                param_name = get_node_text(subchild)
                                break
                        param_type = item.child_by_field_name('type')
                        
                        if param_type:
                            param_type = get_node_text(param_type)
                            metadata['parameters'][param_name] = param_type
                        else:
                            metadata['parameters'][param_name] = None
                            param_type = None

            if child.type == 'reference_type':
                metadata['return_type'] = get_node_text(child)
            
            if not metadata['return_type']:
                return_statement = get_node_by_kind(function_node, ['return_expression'])
                if len(return_statement) > 0:
                    metadata['return_type'] = '<not_specific>'
                else:
                    metadata['return_type'] = None
                
        return metadata
    
    @staticmethod
    def get_class_metadata(class_node, blob=None):
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        metadata = {
            'identifier': '',
            'parameters': [],
        }
        
        assert type(class_node) == tree_sitter.Node
        
        if class_node.type == 'mod_item':
            for child in class_node.children:
                if child.type ==  'identifier':
                    metadata['identifier'] = get_node_text(child)
        
        else:
            identifier = get_node_by_kind(class_node, ['type_identifier'])
            
            metadata['identifier'] = get_node_text(identifier[0])
            if len(identifier) > 1:
                for param in identifier[1:]:
                    metadata['parameters'].append(get_node_text(param))

        return metadata
        

    @staticmethod
    def get_comment_node(function_node):
        comment_node = get_node_by_kind(function_node, kind='comment')
        return comment_node
