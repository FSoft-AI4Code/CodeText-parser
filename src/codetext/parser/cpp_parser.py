from typing import List, Dict, Any

import tree_sitter
import logging

from .language_parser import LanguageParser, get_node_text, get_node_by_kind

logger = logging.getLogger(name=__name__)


class CppParser(LanguageParser):
    
    BLACKLISTED_FUNCTION_NAMES = ['main', 'constructor']
    
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
        docstring_node = CppParser.get_docstring_node(node)
        docstring = '\n'.join(get_node_text(s) for s in docstring_node)
        return docstring
    
    @staticmethod
    def get_docstring_node(node):
        """
        Get docstring node from it parent node.
        C and C++ share the same syntax. Their docstring usually is 1 single block
        Expect length of return list == 1
        
        Args:
            node (tree_sitter.Node): parent node (usually function node) to get its docstring
        Return:
            List: list of docstring nodes (expect==1)
        Example:
            str = '''
                /**
                * Find 2 sum
                *
                * @param nums List number.
                * @param target Sum target.
                * @return postion of 2 number.
                */
                vector<int> twoSum(vector<int>& nums, int target) {
                    ...
                }
            '''
            ...
            print(CppParser.get_docstring_node(function_node))
            
            >>> [<Node type=comment, start_point=(x, y), end_point=(x, y)>]
        """
        docstring_node = []
        
        prev_node = node.prev_sibling
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
    def get_function_list(node):
        res = get_node_by_kind(node, ['function_definition'])
        return res

    @staticmethod
    def get_class_list(node):
        res = get_node_by_kind(node, ['class_specifier'])
        return res
        
    @staticmethod
    def get_comment_node(node):
        """
        Return all comment node inside a parent node
        Args:
            node (tree_sitter.Node)
        Return:
            List: list of comment nodes
        """
        comment_node = get_node_by_kind(node, kind=['comment'])
        return comment_node
    
    @staticmethod
    def get_function_metadata(function_node, blob: str=None) -> Dict[str, Any]:
        """
        Function metadata contains:
            - identifier (str): function name
            - parameters (Dict[str, str]): parameter's name and their type (e.g: {'param_a': 'int'})
            - return_type (str or NoneType): function's return type
        """
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        metadata = {
            'identifier': '',
            'parameters': {},
            'return_type': None,
        }
        assert type(function_node) == tree_sitter.Node
        
        for child in function_node.children:
            if child.type in ['primitive_type', 'type_identifier']:
                metadata['return_type'] = get_node_text(child)
                # search for "function_declarator"
            elif child.type == 'pointer_declarator':
                for subchild in child.children:
                    if subchild.type == 'function_declarator':
                        child = subchild
            if child.type == 'function_declarator':
                for subchild in child.children:
                    if subchild.type in ['qualified_identifier', 'identifier', 'field_identifier']:
                        metadata['identifier'] = get_node_text(subchild)
                    elif subchild.type == 'parameter_list':
                        param_nodes = get_node_by_kind(subchild, ['parameter_declaration'])
                        for param in param_nodes:
                            param_type = param.child_by_field_name('type')
                            param_type = get_node_text(param_type)
                            list_name = get_node_by_kind(param, ['identifier'])
                            if not list_name:
                                continue
                            param_name = get_node_text(list_name[0])
                            metadata['parameters'][param_name] = param_type
                            # for item in param.children:
                                
                            #     if item.type in ['type_identifier', 'primitive_type']:
                            #         param_type = get_node_text(item)
                            #     elif item.type == 'identifier':
                            #         param_identifier = get_node_text(item)

        return metadata

    @staticmethod
    def get_class_metadata(class_node, blob: str=None) -> Dict[str, str]:
        """
        Class metadata contains:
            - identifier (str): class's name
            - parameters (List[str]): inheritance class
        """
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        metadata = {
            'identifier': '',
            'parameters': {},
        }
        assert type(class_node) == tree_sitter.Node
        
        for child in class_node.children:
            if child.type == 'type_identifier':
                metadata['identifier'] = get_node_text(child)
            elif child.type == 'base_class_clause':
                argument_list = []
                for param in child.children:
                    if param.type == 'type_identifier':
                        metadata['parameters'][get_node_text(param)] = None
                        # argument_list.append(get_node_text(param))
                # metadata['parameters'] = argument_list

        return metadata
