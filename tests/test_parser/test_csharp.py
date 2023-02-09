'''test for C# parser'''
import os
import unittest
from pathlib import Path

from src.codetext.parser import CsharpParser
from src.codetext.utils import parse_code


class Test_CsharpParser(unittest.TestCase):
    def setUp(self) -> None:
        with open('tests/test_parser/test_sample/c_sharp_test_sample.cs', 'r') as file:
            self.code_sample = file.read()
        
        tree = parse_code(self.code_sample, 'c#')
        self.root_node = tree.root_node
        
        return super().setUp()

    def test_get_function_list(self):
        root = self.root_node
        
        function_list = CsharpParser.get_function_list(root)
        
        self.assertEqual(len(function_list), 3)  # exclude constructor

    def test_get_class_list(self):
        root = self.root_node
        
        class_list = CsharpParser.get_class_list(root)
        
        self.assertEqual(len(class_list), 1)

    def test_get_docstring(self):
        code_sample = """
        class Vehicle
        {
            public string brand = "Ford";  // Vehicle field
            
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
            
            /* Another method docstring
            in multiple line */
            public void _honk()
            {
                Console.WriteLine("Tuut, tuut!");
            }
        }   
        """
        tree = parse_code(code_sample, 'c#')
        root = tree.root_node
        
        fn1, fn2 = list(CsharpParser.get_function_list(root))

        docs1 = CsharpParser.get_docstring(fn1)
        docs2 = CsharpParser.get_docstring(fn2)
        
        self.assertEqual(docs1, '// <summary>\n// Docstring of a method\n// </summary>\n// <param name="animal_honk">Argument.</param>\n// <returns>\n// None.')
        self.assertEqual(docs2, '/* Another method docstring\n            in multiple line */')
        

    def test_get_function_metadata(self):
        root = self.root_node
        
        function = list(CsharpParser.get_function_list(root))[0]
        metadata = CsharpParser.get_function_metadata(function)

        for key in ['identifier', 'parameters', 'return_type']:
            self.assertTrue(key in metadata.keys())
        self.assertEqual(metadata['parameters'], {'path': 'string', 'filename': 'string'})
        self.assertEqual(metadata['identifier'], 'GetText')
        self.assertEqual(metadata['return_type'], 'string')

    def test_get_class_metadata(self):
        root = self.root_node
        
        classes = list(CsharpParser.get_class_list(root))[0]
        metadata = CsharpParser.get_class_metadata(classes)

        self.assertEqual(metadata['parameters'], ['Animal'])
        self.assertEqual(metadata['identifier'], 'Dog')


if __name__ == '__main__':
    unittest.main()
