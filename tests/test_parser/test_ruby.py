'''test for Ruby parser'''
import os
import unittest
from pathlib import Path

from src.codetext.parser import RubyParser
from src.codetext.utils import parse_code


class Test_RubyParser(unittest.TestCase):
    def setUp(self) -> None:
        with open('tests/test_parser/test_sample/ruby_test_sample.rb', 'r') as file:
            self.code_sample = file.read()
            
        tree = parse_code(self.code_sample, 'ruby')
        self.root_node = tree.root_node

        return super().setUp()

    def test_get_function_list(self):
        root = self.root_node
        
        function_list = RubyParser.get_function_list(root)
        
        self.assertEqual(len(function_list), 1)

    def test_get_class_list(self):
        root = self.root_node
        
        class_list = RubyParser.get_class_list(root)
        
        self.assertEqual(len(class_list), 3)

    def test_get_docstring(self):
        code_sample = """
        module Encryption

            # Search for links.
            #
            # @param query [String] The search query.
            # @option options [String, RedditKit::Subreddit] subreddit The optional subreddit to search.
            def encrypt(string)
                Digest::SHA2.hexdigest(string)
            end
        end
           
        =begin 
        comment line 1
        comment line 2
        =end  
        class Orange
            def initialize
                @juice_available = 100
            end
            def squeeze
                @juice_available -= 50
            end
        end

        orange = Orange.new
        orange.squeeze
        """

        tree = parse_code(code_sample, 'ruby')
        root = tree.root_node
        
        fn = RubyParser.get_function_list(root)[0]
        clas = RubyParser.get_class_list(root)[1]
        
        docs1 = RubyParser.get_docstring(fn)
        docs2 = RubyParser.get_docstring(clas)
        
        self.assertEqual(docs1, '# Search for links.\n#\n# @param query [String] The search query.\n# @option options [String, RedditKit::Subreddit] subreddit The optional subreddit to search.')
        self.assertEqual(docs2, '        comment line 1\n        comment line 2')

    def test_get_function_metadata(self):
        root = self.root_node
        
        function = RubyParser.get_function_list(root)[0]
        metadata = RubyParser.get_function_metadata(function)

        for key in ['identifier', 'parameters', 'return_type']:
            self.assertTrue(key in metadata.keys())
        self.assertEqual(metadata['identifier'], 'search')
        self.assertEqual(metadata['parameters'], ['query', 'options'])
        self.assertEqual(metadata['return_type'], None)
        
    
    def test_metadata_without_return_statement(self):
        code_sample = '''
        def write_code(number_of_errors)
            if number_of_errors > 1
                mood =  "Ask me later"
            else
                mood = puts "No Problem"
            end  
            return mood
        end
        '''
        root = parse_code(code_sample, 'Ruby').root_node
        fn = RubyParser.get_function_list(root)[0]
        metadata = RubyParser.get_function_metadata(fn)
        
        return_type = metadata['return_type']
        self.assertEqual(return_type, '<not_specific>')
        

    def test_get_class_metadata(self):
        root = self.root_node
        
        classes = RubyParser.get_class_list(root)[1]
        metadata = RubyParser.get_class_metadata(classes)

        self.assertEqual(metadata['identifier'], 'Client')
        self.assertEqual(metadata['parameters'], ['API'])
        

if __name__ == '__main__':
    unittest.main()
