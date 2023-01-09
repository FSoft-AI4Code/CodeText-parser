import unittest
from src.codetext.utils import build_language, parse_code


class Test_Utils(unittest.TestCase):
    def test_build_language(self):
        langs = ['python', 'rust']
        for l in langs:
            # clear it later
            build_language(language=l)
    
    def test_parse_code(self):
        sample = """
        def sum_2_num(a, b):
            return a + b
        """
        
        build_language(language='python')
        parse_code(sample, 'python')
    

if __name__ == '__main__':
    unittest.main()