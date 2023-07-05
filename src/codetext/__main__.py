import os
import sys
import argparse
import pkg_resources

from tqdm import tqdm
from .codetext_cli import parse_file, print_result, PL_MATCHING


def get_args():
    parser = argparse.ArgumentParser(description=f"codetext parser {20*'='}")
    
    parser.add_argument('paths', nargs='*', default=['.'],
                        help='list of the filename/paths.')
    parser.add_argument("--version", action="version",
                        version=pkg_resources.get_distribution("codetext").version)
    parser.add_argument("-l", "--language",
                        help='''Target the programming languages you want to
                        analyze.''')
    parser.add_argument("-o", "--output_file",
                        help='''Output file. The output format is inferred
                        from the file extension (e.g. .html), unless it is
                        explicitly specified (e.g. using --xml).
                        ''',
                        type=str)
    parser.add_argument("--json",
                        help='''Generate json output as a transform of the
                        default output''',
                        action="store_true")
    parser.add_argument("--verbose",
                        help='''Print progress bar''',
                        action="store_true")
    
    return parser.parse_args()


def main():
    opt = get_args()
    
    # check path
    for path in opt.paths:
        assert os.path.exists(path) == True, "paths is not valid"
        
        if os.path.isdir(path):
            files = [os.path.join(path, f) for f in os.listdir(path) \
                    if os.path.isfile(os.path.join(path, f))]
        elif os.path.isfile(path):
            files = [path]
            
        if opt.language:
            for file in files[:]:
                filename, file_extension = os.path.splitext(file)
                if file_extension not in PL_MATCHING[opt.language]:
                    files.remove(file)

    output_metadata = {}
    for file in files:
        filename, file_extension = os.path.splitext(file)
        
        if opt.language == None:
            for lang, ext_list in PL_MATCHING.items():
                if file_extension in ext_list:
                    language = lang
                    break
        else:
            language = opt.language

        output = parse_file(file, language=language)
        print_result(
            output, 
            file_name=str(filename).split(os.sep)[-1]+file_extension
        )
        output_metadata[file] = output
    
    if opt.json:
        save_path = opt.output_file
        


if __name__ == '__main__':
    main()
