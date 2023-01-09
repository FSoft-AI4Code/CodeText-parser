'''test for python parser'''
import os
import unittest
from pathlib import Path

from src.codetext.parser import PythonParser
from src.codetext.utils import parse_code


class Test_PythonParser(unittest.TestCase):
    def setUp(self) -> None:        
        with open('tests/test_parser/test_sample/py_test_sample.py', 'r') as file:
            self.code_sample = file.read()
        
        tree = parse_code(self.code_sample, 'python')
        self.root_node = tree.root_node
        return super().setUp()

    def test_get_function_list(self):
        root = self.root_node
        
        function_list = PythonParser.get_function_list(root)
        
        self.assertEqual(len(function_list), 3)

    def test_get_class_list(self):
        root = self.root_node
        
        class_list = PythonParser.get_class_list(root)
        
        self.assertEqual(len(class_list), 1)
    
    def test_is_function_empty(self):
        code_sample = '''
        def test_sample():
            """This is a docstring"""
            # This function is empty
            pass
        '''
        root = parse_code(code_sample, 'python').root_node
        
        function = PythonParser.get_function_list(root)[0]
        
        is_empty = PythonParser.is_function_empty(function)
        self.assertEqual(is_empty, True)

    def test_get_docstring(self):
        code_sample = '''
        def test_sample():
            """This is a docstring"""
            return
        '''
        root = parse_code(code_sample, 'python').root_node
        
        function = PythonParser.get_function_list(root)[0]
        docstring = PythonParser.get_docstring(function, code_sample)
        self.assertEqual(docstring, "This is a docstring")

    def test_get_function_metadata(self):
        code_sample = '''
        def test_sample(arg1: str = "string", arg2 = "another_string"):
            return NotImplement()
        '''
        root = parse_code(code_sample, 'python').root_node
        
        function = list(PythonParser.get_function_list(root))[0]
        metadata = PythonParser.get_function_metadata(function, code_sample)

        self.assertEqual(metadata['parameters'], ['arg1', 'arg2'])
        self.assertEqual(metadata['identifier'], 'test_sample')

    def test_get_class_metadata(self):
        code_sample = '''
        class Sample(ABC):
            def __init__(self):
                pass

            def test_sample(self, arg1: str = "string", arg2 = "another_string"):
                return NotImplement()
        '''
        root = parse_code(code_sample, 'python').root_node
        
        classes = list(PythonParser.get_class_list(root))[0]
        metadata = PythonParser.get_class_metadata(classes, code_sample)

        self.assertEqual(metadata['parameters'], ['ABC'])
        self.assertEqual(metadata['identifier'], 'Sample')
        
    def test_get_comment_list(self):
        root = self.root_node
        
        comment_list = PythonParser.get_comment_node(root)
        comment_list = [node.text.decode() for node in comment_list]
        
        assert comment_list[1] == '# choose the rightmost element as pivot'
        assert comment_list[2] == '# pointer for greater element'
        assert len(comment_list) == 16
        

if __name__ == '__main__':
    unittest.main()
