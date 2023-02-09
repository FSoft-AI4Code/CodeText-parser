import re
from typing import List, Dict, Iterable, Optional, Iterator, Any
import logging

from .language_parser import LanguageParser, get_node_by_kind, get_node_text


logger = logging.getLogger(__name__)


class PythonParser(LanguageParser):
    
    BLACKLISTED_FUNCTION_NAMES = ['__init__', '__name__', '__main__']
    
    @staticmethod
    def get_docstring(node, blob:str=None):
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        docstring_node = PythonParser.get_docstring_node(node)
        
        docstring = ''
        if docstring_node is not None:
            docstring = get_node_text(docstring_node[0])
            docstring = docstring.strip('"').strip("'").strip("#")
        return docstring
    
    @staticmethod
    def get_function_list(node):
        res = get_node_by_kind(node, ['function_definition'])
        return res

    @staticmethod
    def get_class_list(node):
        res = get_node_by_kind(node, ['class_definition'])
        return res
    
    @staticmethod
    def get_docstring_node(node):
        docstring_node = []
        # traverse_type(node, docstring_node, kind=['expression_statement']) #, 'comment'])
        for child in node.children:
            if child.type == 'block':
                for sub_child in child.children:
                    if sub_child.type == 'expression_statement':
                        docstring_node.append(sub_child)

        docstring_node = [node for node in docstring_node if
                          node.type == 'expression_statement' and node.children[0].type == 'string']
        
        if len(docstring_node) > 0:
            return [docstring_node[0].children[0]]  # only take the first block

        return None
    
    @staticmethod
    def get_comment_node(node):
        comment_node = get_node_by_kind(node, kind=['comment', 'expression_statement'])
        for node in comment_node[:]:
            if node.type == 'expression_statement' and node.children[0].type != 'string':
                comment_node.remove(node)
        return comment_node
    
    @staticmethod
    def get_function_metadata(function_node, blob: str=None) -> Dict[str, str]:
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        metadata = {
            'identifier': '',
            'parameters': {},
            'return_type': None,
        }

        for child in function_node.children:
            if child.type == 'identifier':
                metadata['identifier'] = get_node_text(child)
            elif child.type == 'parameters':
                for subchild in child.children:
                    if subchild.type == 'identifier':
                        metadata['parameters'][get_node_text(subchild)] = None
                    elif subchild.type in ['typed_parameter', 'default_parameter', 'typed_default_parameter']:
                        param_type = get_node_by_kind(subchild, ['type'])
                        if param_type:
                            param_type = get_node_text(param_type[0])
                        else:
                            param_type = None
                        param_identifier = get_node_by_kind(subchild, ['identifier'])
                        assert len(param_identifier) != 0, "Empty identifier"
                        param_identifier = get_node_text(param_identifier[0])
                        metadata['parameters'][param_identifier] = param_type
            elif child.type == 'type':
                metadata['return_type'] = get_node_text(child)
                
        if not metadata['return_type']:
            return_statement = get_node_by_kind(function_node, ['return_statement'])
            if len(return_statement) > 0:
                metadata['return_type'] = '<not_specific>'
            else:
                metadata['return_type'] = None
                
        return metadata

    @staticmethod
    def get_class_metadata(class_node, blob: str=None) -> Dict[str, str]:
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        metadata = {
            'identifier': '',
            'parameters': [],
        }
        for child in class_node.children:
            if child.type == 'identifier':
                metadata['identifier'] = get_node_text(child)
            elif child.type == 'argument_list':
                args = []
                argument_list = get_node_text(child).split(',')
                for arg in argument_list:
                    item = re.sub(r'[^a-zA-Z0-9\_]', ' ', arg).split()
                    if len(item) > 0:
                        args.append(item[0].strip())
                metadata['parameters'] = args

        # get __init__ function
        return metadata
