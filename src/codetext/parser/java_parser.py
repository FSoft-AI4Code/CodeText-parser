import re
from typing import List, Dict, Any
import logging

from .language_parser import LanguageParser, get_node_by_kind, get_node_text


logger = logging.getLogger(__name__)


class JavaParser(LanguageParser):

    FILTER_PATHS = ('test', 'tests')

    BLACKLISTED_FUNCTION_NAMES = ['toString', 'hashCode', 'equals', 'finalize', 'notify', 'notifyAll', 'clone']

    @staticmethod
    def get_docstring_node(node):
        """
        Get docstring node from it parent node. Expect return list have length==1
        
        Args:
            node (tree_sitter.Node): parent node (usually function node) to get its docstring
        Return:
            List: list of docstring nodes
        """
        docstring_node = []
        
        if node.prev_sibling:
            prev_node = node.prev_sibling
            if prev_node.type == 'block_comment' or prev_node.type == 'line_comment':
                docstring_node.append(prev_node)
        
        return docstring_node

    @staticmethod
    def get_docstring(node, blob=None):
        """
        Get docstring description for node
        
        Args:
            node (tree_sitter.Node)
            blob (str): original source code which parse the `node`
        Returns:
            str: docstring
        """
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        docstring_node = JavaParser.get_docstring_node(node)

        docstring = ''
        if docstring_node:
            docstring = get_node_text(docstring_node[0])
        return docstring

    @staticmethod
    def get_comment_node(function_node):
        """
        Return all comment node inside a parent node
        Args:
            node (tree_sitter.Node)
        Return:
            List: list of comment nodes
        """
        comment_node = get_node_by_kind(function_node, kind=['line_comment'])
        return comment_node
    
    @staticmethod
    def get_class_list(node):
        res = get_node_by_kind(node, ['class_declaration'])
        return res
    
    @staticmethod
    def get_function_list(node):
        res = get_node_by_kind(node, ['method_declaration'])
        return res
    
    @staticmethod
    def is_method_body_empty(node):
        for c in node.children:
            if c.type in {'method_body', 'constructor_body'}:
                if c.start_point[0] == c.end_point[0]:
                    return True
    
    @staticmethod
    def get_class_metadata(class_node, blob: str=None) -> Dict[str, str]:
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        metadata = {
            'identifier': '',
            'parameters': '',
        }
        argument_list = []
        for child in class_node.children:
            if child.type == 'identifier':
                metadata['identifier'] = get_node_text(child)
            elif child.type == 'superclass' or child.type == 'super_interfaces':
                for subchild in child.children:
                    if subchild.type == 'type_list' or subchild.type == 'type_identifier':
                        argument_list.append(get_node_text(subchild))
                    
        metadata['parameters'] = argument_list
        return metadata

    @staticmethod
    def get_function_metadata(function_node, blob: str=None) -> Dict[str, str]:
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        metadata = {
            'identifier': '',
            'parameters': {},
            'return_type': None
        }
        
        for child in function_node.children:
            if child.type == 'identifier':
                metadata['identifier'] = get_node_text(child)
            elif child.type == 'type_identifier':
                metadata['return_type'] = get_node_text(child)
            elif child.type == 'formal_parameters':
                param_list = get_node_by_kind(child, ['formal_parameter'])  # speed_parameter
                for param in param_list:
                    param_type = get_node_text(param.child_by_field_name('type'))
                    identifier = get_node_text(param.child_by_field_name('name'))
                    metadata['parameters'][identifier] = param_type
        
        return metadata
