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

        for key in ['identifier', 'parameters', 'return_type']:
            self.assertTrue(key in metadata.keys())
        self.assertEqual(metadata['parameters'], {'arg1': 'str', 'arg2': None})
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
        
    def test_metadata_with_return_statement(self):
        code_sample = '''
        def sum2num():
            pass
        '''
        root = parse_code(code_sample, 'python').root_node
        fn = PythonParser.get_function_list(root)[0]
        metadata = PythonParser.get_function_metadata(fn)
        
        return_type = metadata['return_type']
        self.assertEqual(return_type, None)
        
    def test_metadata_with_return_statement(self):
        code_sample = '''
        def sum2num():
            return True
        '''
        root = parse_code(code_sample, 'python').root_node
        fn = PythonParser.get_function_list(root)[0]
        metadata = PythonParser.get_function_metadata(fn)
        
        return_type = metadata['return_type']
        self.assertEqual(return_type, '<not_specific>')
        
    def test_get_parameter(self):
        code_sample = '''
        def sum2num(a: tree_sitter.Node=None, b=None, c:string) -> int:
            pass
        '''
        
        root = parse_code(code_sample, 'python').root_node
        fn = PythonParser.get_function_list(root)[0]
        
        metadata = PythonParser.get_function_metadata(fn)
        parameter = metadata['parameters']
        self.assertEqual(len(parameter.keys()), 3)
        self.assertTrue('a' in parameter.keys())
        self.assertTrue('b' in parameter.keys())
        self.assertTrue('c' in parameter.keys())
        
        return_type = metadata['return_type']
        self.assertEqual(return_type, 'int')
    
    
if __name__ == '__main__':
    unittest.main()
