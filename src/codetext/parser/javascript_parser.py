from typing import List, Dict, Any
import logging

from .language_parser import LanguageParser, get_node_text, get_node_by_kind


logger = logging.getLogger(__name__)


class JavascriptParser(LanguageParser):

    FILTER_PATHS = ('test', 'node_modules')

    BLACKLISTED_FUNCTION_NAMES = ['toString', 'toLocaleString', 'valueOf', 'constructor']

    @staticmethod
    def get_docstring_node(node):
        docstring_node = []
        prev_node = node.prev_sibling
        parent_node = node.parent
                
        if prev_node and prev_node.type == 'comment':
            docstring_node.append(prev_node)
        
        elif parent_node:
            if parent_node.type != 'class_body':  # node not inside a class
                prev_node = parent_node.prev_sibling
                if prev_node and prev_node.type == 'comment':
                    docstring_node.append(prev_node)
            
        return docstring_node
    
    @staticmethod
    def get_docstring(node, blob=None):
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        docstring_node = JavascriptParser.get_docstring_node(node)
        
        docstring = ''
        if docstring_node:
            docstring = get_node_text(docstring_node[0])
        return docstring
    
    @staticmethod
    def get_comment_node(function_node):
        comment_node = get_node_by_kind(function_node, kind=['comment'])
        return comment_node
    
    @staticmethod
    def get_function_list(node):
        function_types = ['function_declaration',
                    'function',
                    'method_definition',
                    'generator_function_declaration',
                    'arrow_function',
                    'generator_function']
        res = get_node_by_kind(node, function_types)
        for node in res[:]:
            if not node.children:
                res.remove(node)

        return res
    
    @staticmethod
    def get_class_list(node):
        res = get_node_by_kind(node, ['class_declaration', 'class'])
        for node in res[:]:
            if not node.children:
                res.remove(node)

        return res

    @staticmethod
    def get_function_metadata(function_node, blob: str=None) -> Dict[str, str]:
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        metadata = {
            'identifier': '',
            'parameters': {},
            'return_type': None,
        }
        param = []
        for child in function_node.children:
            if child.type in ['identifier', 'property_identifier']:
                metadata['identifier'] = get_node_text(child)
            elif child.type == 'formal_parameters':
                params = get_node_by_kind(child, ['identifier'])
                for param in params:
                    identifier = get_node_text(param)
                    metadata['parameters'][identifier] = None  # JS not have type define
        
        return_statement = get_node_by_kind(function_node, ['return_statement'])
        if len(return_statement) > 0:
            metadata['return_type'] = '<not_specific>'
            
        if function_node.type in ["function",
                                  "arrow_function",
                                  "generator_function"]:
            # function inside object property or variable declarator
            identifier = function_node.prev_named_sibling
            if identifier:
                if identifier.type in ["identifier"]:
                    metadata["identifier"] = identifier.text.decode()
        
        return metadata

    @staticmethod
    def get_class_metadata(class_node, blob=None):
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        metadata = {
            'identifier': '',
            'parameters': {},
        }
        param = []
        for child in class_node.children:
            if child.type == 'identifier':
                metadata['identifier'] = get_node_text(child)
            elif child.type == 'class_heritage':
                for subchild in child.children:
                    if subchild.type == 'identifier':
                        metadata['parameters'][get_node_text(subchild)] = None
                        # param.append(get_node_text(subchild))
                        
        # metadata['parameters'] = param
        return metadata
