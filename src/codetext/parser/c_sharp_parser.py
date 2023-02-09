from typing import List, Dict, Any
import tree_sitter
import logging

from .language_parser import LanguageParser, get_node_by_kind, get_node_text

logger = logging.getLogger(name=__name__)


class CsharpParser(LanguageParser):
    
    BLACKLISTED_FUNCTION_NAMES = []
    
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
        docstring_node = CsharpParser.get_docstring_node(node)
        docstring = '\n'.join(get_node_text(s) for s in docstring_node)
        return docstring
    
    @staticmethod
    def get_docstring_node(node):
        """
        Get docstring node from it parent node.
        C# docstring is written line by line and stay outside it own node, see example below.
        
        Args:
            node (tree_sitter.Node): parent node (usually function node) to get its docstring
        Return:
            List: list of docstring nodes
        Example:
            str = '''
                // <summary>
                // Docstring of a method
                // </summary>
                // <param name="animal_honk">Argument.</param>
                // <returns>
                // None.
                public void honk(string animal_honk)
                {                    
                    Console.WriteLine(animal_honk);
                    Console.WriteLine("Tuut, tuut!");
                }
            '''
            ...
            print(C_sharp.get_docstring_node(function_node))
            
            >>> [<Node type=comment, start_point=(5, 12), end_point=(5, 24)>, \
                <Node type=comment, start_point=(6, 12), end_point=(6, 36)>, \
                <Node type=comment, start_point=(7, 12), end_point=(7, 25)>, \
                <Node type=comment, start_point=(8, 12), end_point=(8, 58)>, \
                <Node type=comment, start_point=(9, 12), end_point=(9, 24)>, \
                <Node type=comment, start_point=(10, 12), end_point=(10, 20)>]
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
    def get_function_list(node):
        res = get_node_by_kind(node, ['local_function_statement', 'method_declaration'])
        # We don't use "constructor_declaration"
        return res

    @staticmethod
    def get_class_list(node):
        res = get_node_by_kind(node, ['class_declaration'])
        return res

    @staticmethod
    def get_function_metadata(function_node, blob: str=None) -> Dict[str, Any]:
        """
        Function metadata contains:
            - identifier (str): function name
            - parameters (Dict[str, str]): parameter's name and their type (e.g: {'param_a': 'int'})
            - type (str): type
        """
        if blob:
            logger.info('From version `0.0.6` this function will update argument in the API')
        metadata = {
            'identifier': '',
            'parameters': {},
            'return_type': None
        }
        assert type(function_node) == tree_sitter.Node
        
        for child in function_node.children:
            if child.type == 'predefined_type':
                metadata['return_type'] = get_node_text(child)
            elif child.type == 'identifier':
                metadata['identifier'] = get_node_text(child)
            elif child.type == 'parameter_list':
                for param_node in child.children:
                    param_nodes = get_node_by_kind(param_node, ['parameter'])
                    for param in param_nodes:
                        param_type = get_node_text(param.children[0])
                        param_identifier = get_node_text(param.children[1])
                    
                        metadata['parameters'][param_identifier] = param_type
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
            'parameters': '',
        }
        assert type(class_node) == tree_sitter.Node
        
        for child in class_node.children:
            if child.type == 'identifier':
                metadata['identifier'] = get_node_text(child)
            elif child.type == 'base_list':
                argument_list = []
                for arg in child.children:
                    if arg.type == 'identifier':
                        argument_list.append(get_node_text(arg))
                metadata['parameters'] = argument_list

        return metadata
    
