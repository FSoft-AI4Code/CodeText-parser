import re
from typing import List, Dict, Any
import tree_sitter
import logging

from .language_parser import LanguageParser, get_node_text, get_node_by_kind


logger = logging.getLogger(__name__)


class PhpParser(LanguageParser):

    FILTER_PATHS = ('test', 'tests')

    BLACKLISTED_FUNCTION_NAMES = ['__construct', '__destruct', '__call', '__callStatic',
                                  '__get', '__set', '__isset', '__unset',
                                  '__sleep', '__wakeup', '__toString', '__invoke',
                                  '__set_state', '__clone', '__debugInfo', '__serialize',
                                  '__unserialize']

    @staticmethod
    def get_docstring(node, blob: str=None) -> str:
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        docstring_node = PhpParser.get_docstring_node(node)
        
        docstring = ''
        if docstring_node:
            docstring = get_node_text(docstring_node[0])
        
        return docstring
    
    @staticmethod
    def get_docstring_node(node):
        docstring_node = []
        
        if node.prev_sibling is not None:
            prev_node = node.prev_sibling
            if prev_node.type == 'comment':
                docstring_node.append(prev_node)
        
        return docstring_node
    
    @staticmethod
    def get_comment_node(function_node):
        comment_node = get_node_by_kind(function_node, kind='comment')
        return comment_node
    
    @staticmethod
    def get_class_list(node):
        res = get_node_by_kind(node, ['class_declaration', 'trait_declaration'])
        return res
    
    @staticmethod
    def get_function_list(node):
        res = get_node_by_kind(node, ['function_definition', 'method_declaration'])
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

        for n in function_node.children:
            if n.type == 'name':
                metadata['identifier'] = get_node_text(n)
            if n.type in ['union_type', 'intersection_type']:
                metadata['return_type'] = get_node_text(n)
            elif n.type == 'formal_parameters':
                for param_node in n.children:
                    if param_node.type in ['simple_parameter', 'variadic_parameter', 'property_promotion_parameter']:
                        identifier = get_node_text(param_node.child_by_field_name('name'))
                        param_type = param_node.child_by_field_name('type')
                        if param_type:
                            param_type = get_node_text(param_type)
                            metadata['parameters'][identifier] = param_type
                        else:
                            metadata['parameters'][identifier] = None
                        
        if not metadata['return_type']:
            return_statement = get_node_by_kind(function_node, ['return_statement'])
            if len(return_statement) > 0:
                metadata['return_type'] = '<not_specific>'
            else:
                metadata['return_type'] = None

        return metadata

    
    @staticmethod
    def get_class_metadata(class_node, blob: str=None):
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        metadata = {
            'identifier': '',
            'parameters': '',
        }
        assert type(class_node) == tree_sitter.Node
        
        for child in class_node.children:
            if child.type == 'name':
                metadata['identifier'] = get_node_text(child)
            elif child.type == 'base_clause':
                argument_list = []
                for param in child.children:
                    if param.type == 'name':
                        argument_list.append(get_node_text(param))
                metadata['parameters'] = argument_list 
    
        return metadata
