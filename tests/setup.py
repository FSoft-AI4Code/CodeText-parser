from ..src.codetext.utils import build_language
from tree_sitter_languages import get_language, get_parser

if __name__ == '__main__':
    lang_list = ['python', 'cpp', 'java', 'c-sharp', 'ruby', 'rust', 'javascript', 'php', 'go']
    
    for lang in lang_list:
        # build_language(lang)
        try:
            get_parser(get_language(lang))
        except:
            build_language(lang)
