import os

def readCodeFile(filePath):
    """
    Reads a C or header file and returns its contents as a list of lines.

    Args:
        filePath (str): Path to the source file.

    Returns:
        List[Dict]: A list of dictionaries, each with 'lineNumber' and 'codeLine'.
    """
    if not os.path.exists(filePath):
        raise FileNotFoundError(f"Code file not found: {filePath}")

    if not (filePath.endswith(".c") or filePath.endswith(".h")):
        raise ValueError("Only .c or .h files are allowed.")

    codeLines = []
    with open(filePath, 'r') as file:
        for idx, line in enumerate(file, start=1):
            codeLines.append({
                "lineNumber": idx,
                "codeLine": line.strip()
            })

    return codeLines
