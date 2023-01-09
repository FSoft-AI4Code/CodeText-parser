<div align="center">

<p align="center">
  <img src="https://avatars.githubusercontent.com/u/115590550?s=200&v=4" width="220px" alt="logo">
</p>

**CodeText-parser**
______________________________________________________________________


<!-- Badge start -->
| Branch 	| Build 	| Unittest 	| Linting 	| Release 	| License 	|
|--------	|-------	|----------	|---------	|---------	|---------	|
| main   	|       	| [![Unittest](https://github.com/AI4Code-Research/CodeText-parser/actions/workflows/unittest.yml/badge.svg)](https://github.com/AI4Code-Research/CodeText-parser/actions/workflows/unittest.yml) |       	| [![release](https://img.shields.io/pypi/v/codetext)](https://pypi.org/project/codetext/) [![pyversion](https://img.shields.io/pypi/pyversions/codetext)](https://pypi.org/project/codetext/)| [![license](https://img.shields.io/github/license/AI4Code-Research/CodeText-parser)](https://github.com/AI4Code-Research/CodeText-parser/blob/main/LICENSES.txt) |
<!-- Badge end -->
</div>

______________________________________________________________________

**Code-Text data toolkit** contains multilingual programming language parsers for the extract from raw source code into multiple levels of pair data (code-text) (e.g., function-level, class-level, inline-level). 

# Installation
Setup environment and install dependencies and setup by using `install_env.sh`
```bash
bash -i ./install_env.sh
```
then activate conda environment named "code-text-env"
```bash
conda activate code-text-env
```

*Setup for using parser*
```bash
pip install codetext
```

# Getting started

## Build your language
Auto build tree-sitter into `<language>.so` located in `/tree-sitter/`
```python
from codetext.utils import build_language

language = 'rust'
build_language(language)


# INFO:utils:Not found tree-sitter-rust, attempt clone from github
# Cloning into 'tree-sitter-rust'...
# remote: Enumerating objects: 2835, done. ...
# INFO:utils:Attempt to build Tree-sitter Language for rust and store in .../tree-sitter/rust.so
```

## Language Parser
We supported 10 programming languages, namely `Python`, `Java`, `JavaScript`, `Golang`, `Ruby`, `PHP`, `C#`, `C++`, `C` and `Rust`.

Setup
```python
from codetext.utils import parse_code

raw_code = """
/**
* Sum of 2 number
* @param a int number
* @param b int number
*/
double sum2num(int a, int b) {
    return a + b;
}
"""

root = parse_code(raw_code, 'cpp')
root_node = root.root_node
```

Get all function nodes inside a specific node, use:
```python
from codetext.utils.parser import CppParser

function_list = CppParser.get_function_list(root_node)
print(function_list)

# [<Node type=function_definition, start_point=(6, 0), end_point=(8, 1)>]

```

Get function metadata (e.g. function's name, parameters, (optional) return type)
```python
function = function_list[0]

metadata = CppParser.get_function_metadata(function, raw_code)

# {'identifier': 'sum2num', 'parameters': {'a': 'int', 'b': 'int'}, 'type': 'double'}
```
Get docstring (documentation) of a function
```python
docstring = CppParser.get_docstring(function, code_sample)

# ['Sum of 2 number \n@param a int number \n@param b int number']
```

We also provide 2 command for extract class object
```python
class_list = CppParser.get_class_list(root_node)
# and
metadata = CppParser.get_metadata_list(root_node)
```
