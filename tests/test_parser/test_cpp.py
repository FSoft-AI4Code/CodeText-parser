'''test for C++ parser'''
import os
import unittest
from pathlib import Path

from src.codetext.parser import CppParser
from src.codetext.utils import parse_code


class Test_CppParser(unittest.TestCase):
    def setUp(self) -> None:
        with open('tests/test_parser/test_sample/cpp_test_sample.cpp', 'r') as file:
            self.code_sample = file.read()
            
        tree = parse_code(self.code_sample, 'c++')
        self.root_node = tree.root_node

        return super().setUp()

    def test_get_function_list(self):
        root = self.root_node
        
        function_list = CppParser.get_function_list(root)
        
        self.assertEqual(len(function_list), 3)
        
    def test_get_class_list(self):
        root = self.root_node
        
        class_list = CppParser.get_class_list(root)
        
        self.assertEqual(len(class_list), 2)

    def test_get_function_metadata(self):
        root = self.root_node
        
        function = list(CppParser.get_function_list(root))[0]
        metadata = CppParser.get_function_metadata(function)

        for key in ['identifier', 'parameters', 'return_type']:
            self.assertTrue(key in metadata.keys(), "Missing {}".format(key))
        self.assertEqual(metadata['parameters'], {'a': 'int', 'b': 'int'})
        self.assertEqual(metadata['identifier'], 'sum2number')
        self.assertEqual(metadata['return_type'], 'int')
    
    def test_get_class_metadata(self):
        root = self.root_node
        
        classes = list(CppParser.get_class_list(root))[0]
        metadata = CppParser.get_class_metadata(classes)

        self.assertEqual(metadata['parameters'], ['Vehicle', 'B'])
        self.assertEqual(metadata['identifier'], 'Car')

    def test_get_docstring(self):
        code_sample = """
        /**
        * Find 2 sum
        *
        * @param nums List number.
        * @param target Sum target.
        * @return postion of 2 number.
        */
        vector<int> twoSum(vector<int>& nums, int target) {
            map<int,int> m;
            vector<int> v;
            int n= nums.size();
            for(int i=0;i<n;i++)
            {
                
                    int diff = target - nums[i];
                    if(m.find(diff) != m.end())
                    {
                    auto p = m.find(diff);        
                    v.push_back(p->second);
                    v.push_back(i);
                    }
                    m.insert(make_pair(nums[i],i));
            }

            return v;
        }

        // Comment in
        // multiple line
        // of the function sum
        double sum2num(int a, int b) {
            return a + b;
        }
        """
        tree = parse_code(code_sample, 'c++')
        root = tree.root_node
        
        fn1, fn2 = list(CppParser.get_function_list(root))

        docs1 = CppParser.get_docstring(fn1)
        docs2 = CppParser.get_docstring(fn2)
        
        self.assertEqual(docs1, '/**\n        * Find 2 sum\n        *\n        * @param nums List number.\n        * @param target Sum target.\n        * @return postion of 2 number.\n        */')
        self.assertEqual(docs2, '// Comment in\n// multiple line\n// of the function sum')


if __name__ == '__main__':
    unittest.main()
