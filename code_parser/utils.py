# code_parser/utils.py

import re
import os

def remove_comments(code: str) -> str:
    """
    Removes single-line (//) and multi-line (/* */) comments from C code.
    """
    code = re.sub(r'//.*', '', code)
    code = re.sub(r'/\*[\s\S]*?\*/', '', code)
    return code


def is_c_file(filename: str) -> bool:
    """
    Checks if a file has a .c or .h extension.
    """
    return filename.endswith('.c') or filename.endswith('.h')


def read_code_file(filepath: str) -> str:
    """
    Reads a C or header file from disk.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
