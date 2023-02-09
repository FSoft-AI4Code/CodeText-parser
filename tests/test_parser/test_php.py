'''test for PHP parser'''
import os
import unittest
from pathlib import Path

from src.codetext.parser import PhpParser
from src.codetext.utils import parse_code


class Test_PhpParser(unittest.TestCase):
    def setUp(self) -> None:
        with open('tests/test_parser/test_sample/php_test_sample.php', 'r') as file:
            self.code_sample = file.read()
            
        tree = parse_code(self.code_sample, 'php')
        self.root_node = tree.root_node

        return super().setUp()

    def test_get_function_list(self):
        root = self.root_node
        
        function_list = PhpParser.get_function_list(root)
        
        self.assertEqual(len(function_list), 3)

    def test_get_class_list(self):
        root = self.root_node
        
        class_list = PhpParser.get_class_list(root)
        
        self.assertEqual(len(class_list), 1)

    def test_get_docstring(self):
        code_sample = """
        <?php
        /**
        * Get all image nodes.
        *
        * @param \DOMNode     $node       The \DOMDocument instance
        * @param boolean      $strict     If the document has to be valid
        *
        * @return \DOMNode
        */
        function getImageNodes(\DOMNode $node, $strict = true): \DOMNode
        {
            // ...
            return $node;
        }
        ?>
        """

        tree = parse_code(code_sample, 'php')
        root = tree.root_node
        
        fn = PhpParser.get_function_list(root)[0]

        docs = PhpParser.get_docstring(fn)
        
        self.assertEqual(docs, '/**\n        * Get all image nodes.\n        *\n        * @param \\DOMNode     $node       The \\DOMDocument instance\n        * @param boolean      $strict     If the document has to be valid\n        *\n        * @return \\DOMNode\n        */')
        

    def test_get_function_metadata(self):
        root = self.root_node
        
        function = list(PhpParser.get_function_list(root))[1]
        metadata = PhpParser.get_function_metadata(function)

        for key in ['identifier', 'parameters', 'return_type']:
            self.assertTrue(key in metadata.keys())
        self.assertEqual(metadata['parameters'],  {'$params': 'array', '$connectionOptions': 'array'})
        self.assertEqual(metadata['identifier'], 'constructDsn')
        self.assertEqual(metadata['return_type'], 'string')
        
    def test_metadata_with_return_statement(self):
        code_sample = '''
        <?php
        function sum($a, $b): {
            return $a + $b;
        }
        ?>
        '''
        root = parse_code(code_sample, 'PHP').root_node
        fn = PhpParser.get_function_list(root)[0]
        metadata = PhpParser.get_function_metadata(fn)
        
        return_type = metadata['return_type']
        self.assertEqual(return_type, '<not_specific>')

    def test_metadata_without_return_statement(self):
        code_sample = '''
        <?php
        function sum($a, $b): {
        }
        ?>
        '''
        root = parse_code(code_sample, 'PHP').root_node
        fn = PhpParser.get_function_list(root)[0]
        metadata = PhpParser.get_function_metadata(fn)
        
        return_type = metadata['return_type']
        self.assertEqual(return_type, None)

    def test_get_class_metadata(self):
        root = self.root_node
        
        classes = list(PhpParser.get_class_list(root))[0]
        metadata = PhpParser.get_class_metadata(classes)

        self.assertEqual(metadata['parameters'], ['AbstractSQLServerDriver'])
        self.assertEqual(metadata['identifier'], 'Driver')
        

if __name__ == '__main__':
    unittest.main()
