import os
from typing import List, Dict

from tabulate import tabulate

from .parser import *
from .utils import parse_code


def parse_file(file_path: str, language: str = None, verbose: bool = False) -> List:
    assert language != None, "Auto detect is not implemented, please specify language"
    language = str(language).lower()
    # assert (language in SUPPORT_LANGUAGE) == True, f"{language} is not supported"
    assert os.path.isfile(file_path) == True, "File not found"

    if verbose:
        print(50 * "=")
        print("Parse code into tree-sitter node")

    content: str = open(file_path, "r").read()
    root_node = parse_code(raw_code=content, language=language).root_node

    if language == "python":
        parser: LanguageParser = PythonParser
    elif language == "java":
        parser: LanguageParser = JavaParser
    elif language == "javascript":
        parser: LanguageParser = JavascriptParser
    elif language == "go":
        parser: LanguageParser = GoParser
    elif language in ["c", "c++"]:
        parser: LanguageParser = CppParser
    elif language == "c#":
        parser: LanguageParser = CsharpParser
    elif language == "rust":
        parser: LanguageParser = RustParser
    elif language == "ruby":
        parser: LanguageParser = RubyParser
    elif language == "php":
        parser: LanguageParser = PhpParser
    else:
        raise KeyError(f"{language} is not supported")

    if verbose:
        print(50 * "=")
        print("Get node detail")

    cls_list = parser.get_class_list(root_node)
    method_list = []
    cls_metadata = []
    for _cls in cls_list:
        cls_info = parser.get_class_metadata(_cls)
        cls_info["code"] = get_node_text(_cls)

        cls_method = []
        current_class_methods = parser.get_function_list(_cls)
        for method in current_class_methods:
            method_info = parser.get_function_metadata(method)
            method_info['code'] = get_node_text(method)
            cls_method.append(method_info)

        cls_info["method"] = cls_method
        cls_metadata.append(cls_info)
        method_list.extend(current_class_methods)

    fn_list: List = parser.get_function_list(root_node)
    for node in fn_list[:]:
        if node in method_list:
            fn_list.remove(node)

    fn_metadata = []
    for fn in fn_list:
        fn_metadata.append(parser.get_function_metadata(fn))

    output_metadata = {"class": cls_metadata, "function": fn_metadata}

    return output_metadata


def print_result(res: Dict, file_name: str = "no_name_file"):
    # ======== Print file name ========
    print("File {name} analyzed:".format(name=file_name))
    print(50 * "=")

    # ========= Summary =========
    print("Number of class    : {length}".format(length=len(res["class"])))
    print("Number of function : {length}".format(length=len(res["function"])))
    print(50 * "-" + "\n")

    # ========= Print class & method =========
    cls_headers = ["#", "Class", "Arguments"]
    cls_method_headers = ["#", "Method name", "Paramters", 
                          "Type", "Return type", "Throws"]
    cls_info = []
    method_info = {}
    for cls_idx, _cls in enumerate(res["class"]):
        cls_max_length = max(1, len(_cls["parameters"].keys()))
        for i in range(cls_max_length):
            clslist = [""] * len(cls_headers)
            clslist[0] = cls_idx if i < 1 else ""
            clslist[1] = _cls["identifier"] if i < 1 else ""
            if _cls["parameters"].keys():
                clslist[2] = list(_cls["parameters"].keys())[i]
            cls_info.append(clslist)

        _method_info = []
        for idx, method in enumerate(_cls["method"]):
            max_length = max(1, len(method["parameters"].keys()))
            for i in range(max_length):
                sublist = [""] * len(cls_method_headers)
                sublist[0] = idx if i < 1 else ""
                sublist[1] = method["identifier"] if i < 1 else ""
                if method["parameters"].keys():
                    sublist[2] = list(method["parameters"].keys())[i]
                    sublist[3] = list(method["parameters"].values())[i]
                sublist[4] = (
                    method["return_type"]
                    if i <= 1 and method["return_type"] != "<not_specific>"
                    else ""
                )
                sublist[5] = (
                    method["throws"]
                    if i <= 1 and "throws" in method.keys()
                    else ""
                )
                _method_info.append(sublist)

            method_info[file_name] = [_cls["identifier"], _method_info]

    if cls_info:
        print("Class summary:")
        print(tabulate(cls_info, headers=cls_headers, tablefmt="outline"))
        print("\n")

        for _, info in method_info.items():
            name, info = info
            print("Class analyse: {name}".format(name=name))
            print(tabulate(info, headers=cls_method_headers, tablefmt="outline"))
            print("\n")

    # ========= Print stand alone function =========
    fn_headers = ["#", "Function name", "Paramters", "Type", "Return type"]
    function_info = []

    for idx, fn in enumerate(res["function"]):
        max_length = max(1, len(fn["parameters"].keys()))
        for i in range(max_length):
            sublist = [""] * len(fn_headers)
            sublist[0] = idx if i < 1 else ""
            sublist[1] = fn["identifier"] if i < 1 else ""
            if fn["parameters"].keys():
                sublist[2] = list(fn["parameters"].keys())[i]
                sublist[3] = list(fn["parameters"].values())[i]
            sublist[4] = (
                fn["return_type"]
                if i <= 1 and fn["return_type"] != "<not_specific>"
                else ""
            )
            function_info.append(sublist)

    if function_info:
        print("Function analyse:")
        print(tabulate(function_info, headers=fn_headers, tablefmt="outline"))
        print("\n")

    elif not method_info:
        print("File empty")
        print("\n")


PL_MATCHING = {
    "Java": [".java"],
    "JavaScript": [
        ".js",
        "._js",
        ".bones",
        ".es6",
        ".jake",
        ".jsb",
        ".jscad",
        ".jsfl",
        ".jsm",
        ".jss",
        ".njs",
        ".pac",
        ".sjs",
        ".ssjs",
        ".xsjs",
        ".xsjslib",
    ],
    "Python": [
        ".py",
        ".bzl",
        ".gyp",
        ".lmi",
        ".pyde",
        ".pyp",
        ".pyt",
        ".pyw",
        ".tac",
        ".wsgi",
        ".xpy",
    ],
    "PHP": [".php", ".aw", ".ctp", ".php3", ".php4", ".php5", ".phps", ".phpt"],
    "Go": [".go"],
    "Rust": [".rs", ".rs.in"],
    "Ruby": [
        ".rb",
        ".builder",
        ".gemspec",
        ".god",
        ".irbrc",
        ".jbuilder",
        ".mspec",
        ".podspec",
        ".rabl",
        ".rake",
        ".rbuild",
        ".rbw",
        ".rbx",
        ".ru",
        ".ruby",
        ".thor",
        ".watchr",
    ],
    "C": [".c", ".cats", ".h", ".idc", ".w"],
    "C#": [".cs", ".cake", ".cshtml", ".csx"],
    "C++": [
        ".cpp",
        ".c++",
        ".cc",
        ".cp",
        ".cxx",
        ".h++",
        ".hh",
        ".hpp",
        ".hxx",
        ".inl",
        ".ipp",
        ".tcc",
        ".tpp",
        ".C",
        ".H",
    ],
}
