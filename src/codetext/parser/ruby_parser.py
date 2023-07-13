import re
from typing import List, Dict, Any

import tree_sitter
import logging

from .language_parser import LanguageParser, get_node_text, get_node_by_kind
# from function_parser.parsers.commentutils import get_docstring_summary


logger = logging.getLogger(__name__)


class RubyParser(LanguageParser):

    FILTER_PATHS = ('test', 'vendor')

    BLACKLISTED_FUNCTION_NAMES = ['initialize', 'to_text', 'display', 'dup', 'clone', 'equal?', '==', '<=>',
                                  '===', '<=', '<', '>', '>=', 'between?', 'eql?', 'hash']

    @staticmethod
    def get_function_list(node):
        res = get_node_by_kind(node, ['method',
                                      'singleton_method'])
        return res
    
    @staticmethod
    def get_class_list(node):
        res = get_node_by_kind(node, ['class', 'module'])
        
        # remove class keywords
        for node in res[:]:
            if not node.children:
                res.remove(node)

        return res

    @staticmethod
    def get_docstring_node(node) -> str:
        docstring_node = []
        
        prev_node = node.prev_sibling        
        if not prev_node or prev_node.type != 'comment':
            parent_node = node.parent
            if parent_node:
                prev_node = parent_node.prev_sibling

        if prev_node and prev_node.type == 'comment':
            docstring_node.append(prev_node)
            prev_node = prev_node.prev_sibling
                
        while prev_node and prev_node.type == 'comment':
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
        docstring_node = RubyParser.get_docstring_node(node)
        docstring = []
        for item in docstring_node:
            doc = get_node_text(item)
            doc_lines = doc.split('\n')
            for line in doc_lines:
                if '=begin' in line or '=end' in line:
                    continue
                docstring.append(line)
            
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
        assert function_node.type in ['method', 'singleton_method']
        
        for child in function_node.children:
            if child.type == 'identifier':
                metadata['identifier'] = get_node_text(child)
            elif child.type in ['method_parameters', 'parameters', 'bare_parameters']:
                params = get_node_by_kind(child, ['identifier'])
                for item in params:
                    metadata['parameters'][get_node_text(item)] = None

        if not metadata['return_type']:
            return_statement = get_node_by_kind(function_node, ['return'])
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
            'parameters': {},
        }
        
        assert type(class_node) == tree_sitter.Node
        
        for child in class_node.children:
            if child.type == 'constant':
                metadata['identifier'] = get_node_text(child)
            if child.type == 'superclass':
                for subchild in child.children:
                    if subchild.type == 'constant':
                        metadata['parameters'][get_node_text(subchild)] = None

        return metadata
        

    @staticmethod
    def get_comment_node(function_node):
        comment_node = get_node_by_kind(function_node, kind='comment')
        return comment_node
    
    @staticmethod
    def get_action_list(action_node):
        call_nodes =  get_node_by_kind(action_node, ['call'])
        res = []
        for call_node in call_nodes:
            if get_node_by_kind(call_node, ["do_block"]):
                res.append(call_node)
        # print(res)
        return res
    
    @staticmethod
    def get_action_metadata(action_node):
        metadata = {
            'identifier': '',
            'parameters': {},
            'return_type': None,
        }
        
        for child in action_node.children:
            if child.type in ["identifier"]:
                metadata['identifier'] = get_node_text(child)
            if child.type in ["argument_list"]:
                symbol =  get_node_by_kind(child, ["simple_symbol"])
                if symbol:
                    metadata['identifier'] += get_node_text(symbol[0])
        
        parameters =  get_node_by_kind(action_node, ["block_parameters"])
        
        if parameters:
            for param in get_node_by_kind(parameters[0], ["identifier"]):
                param_name = get_node_text(param)
                metadata['parameters'].update({param_name : None})
        
        return metadata
    
