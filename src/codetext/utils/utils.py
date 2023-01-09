import json
import inspect
import sys
import os
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any, Union

import tree_sitter
from tree_sitter import Language, Parser


logger = logging.getLogger('utils')
logging.basicConfig(level = logging.INFO)


SUPPORTED_LANGUAGE = ['python', 'java', 'javascript', 'ruby', 'go', 'c', 'cpp', 'c++', 'c#', 'c_sharp', 'php', 'rust']


def build_language(language: str, save_path: str=None):
    """
    Build tree-sitter language
    
    Args:
        language (str): java, python, cpp, c_sharp, etc
        save_path (str): save path (default create a `/tree-sitter/` dir)
    """
    language = str(language).lower()
    if language == 'c#':
        language = 'c_sharp'
    elif language == 'c++':
        language = 'cpp'

    assert language.lower() in SUPPORTED_LANGUAGE, f"Expect {language} in {SUPPORTED_LANGUAGE}"
    if not save_path:
        calling_script_path = Path(inspect.getframeinfo(sys._getframe(1)).filename)
        save_path = calling_script_path.parent
        
    # create `tree-sitter` dir
    ts_path = os.path.join(save_path, 'tree-sitter')
    if not os.path.exists(ts_path):
        logger.warning(
            f"Not found `tree-sitter` folder, create new one in {ts_path}"
        )
        os.mkdir(ts_path)
    
    # check `tree-sitter/tree-sitter-<language>`
    ts_lang_path = os.path.join(ts_path, 'tree-sitter-'+language.replace('_', '-'))
    if not os.path.exists(ts_lang_path):
        logger.warning(
            f"Not found `tree-sitter-{language.replace('_', '-')}`, attempt clone from github to {ts_path}"
        )
        command = f"cd {ts_path}; git clone https://github.com/tree-sitter/tree-sitter-{language.replace('_', '-')}.git"
        subprocess.Popen(command ,shell=True).wait()
        
        assert os.path.exists(ts_lang_path)==True, f"Unable to find {language} tree-sitter in {ts_path}"
    
    # if language == 'c-sharp': language = 'c_sharp'
    lang_path = os.path.join(save_path, 'tree-sitter', f'{language}.so')
    if not os.path.exists(lang_path):
        logger.info(
            f"Attempt to build Tree-sitter Language for {language} and store in {lang_path}"
        )
        Language.build_library(lang_path, [ts_lang_path])
        assert os.path.exists(lang_path)==True
    else:
        logger.info(f"Language already existed!")
        
    
def parse_code(raw_code: str, language: str='Auto', tree_sitter_path: str=None) -> tree_sitter.Tree:
    """
    Auto parse raw code into `tree_sitter.Tree`
    
    Args:
        raw_code (str): Raw source code need to parse
        language (str): Language to load parser
    """
    # TODO: auto detect language
    if language == 'Auto':
        raise NotImplemented("This feature is underdevelopment")
    language = str(language).lower()
    if language == 'c#':
        language = 'c_sharp'
    elif language == 'c++':
        language = 'cpp'
    assert language in SUPPORTED_LANGUAGE, f"Expect {language} in {SUPPORTED_LANGUAGE}"
    
    if tree_sitter_path:
        load_path = tree_sitter_path
    else:
        calling_script_path = Path(inspect.getframeinfo(sys._getframe(1)).filename)
        load_path = str(calling_script_path.parent)

    ts_lang_path = os.path.join(load_path, 'tree-sitter', f'{language}.so')
    if not os.path.exists(ts_lang_path):
        logger.warning(f"Not found `{language}.so` in `{load_path}/tree-sitter/`, attemp to build language")
        build_language(language, load_path)
        
    parser = Parser()
    language = Language(load_path + f"/tree-sitter/{language}.so", language)
    parser.set_language(language)
    
    if isinstance(raw_code, str):
        tree = parser.parse(bytes(raw_code, 'utf8'))
        return tree
    else:
        raise ValueError(f"Expect `str`, got {type(raw_code)}")
