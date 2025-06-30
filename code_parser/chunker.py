import logging
from config import CHUNK_LINE_LIMIT
from pycparser import c_parser
from pycparser.plyparser import ParseError
from code_parser.utils import remove_comments, read_code_file
logger = logging.getLogger(__name__)

def split_into_chunks(code_lines, chunk_size=CHUNK_LINE_LIMIT):
    """Fallback: chunk raw lines by size if parsing fails."""
    chunks = []
    for i in range(0, len(code_lines), chunk_size):
        chunk = code_lines[i:i+chunk_size]
        chunks.append('\n'.join(chunk))
    total_chunks = len(code_lines) // chunk_size + 1
    logger.info("Line-based fallback chunking: %d chunks of ~%d lines", total_chunks, chunk_size)    
    return chunks

def extract_function_chunks(filepath: str):
    """
    Parses a C file and extracts each function definition as a chunk.
    Falls back to line-based splitting if parsing fails.
    """
    logger.info("Reading file: %s", filepath)
    with open(filepath, "r") as f:
        raw_code = f.read()
    raw_code = read_code_file(filepath)


    clean_code = remove_comments(raw_code)
    lines = clean_code.splitlines()
    logger.debug("Total lines in code: %d", len(lines))
    try:
        parser = c_parser.CParser()
        ast = parser.parse(clean_code)

        chunks = []
        for ext in ast.ext:
            if ext.__class__.__name__ == "FuncDef":
                start_line = ext.coord.line - 1
                func_header = lines[start_line].strip()
                body_lines = []

                # Naively collect function lines by counting braces
                brace_count = 0
                for i in range(start_line, len(lines)):
                    line = lines[i]
                    body_lines.append(line)
                    brace_count += line.count("{") - line.count("}")
                    if brace_count == 0 and "{" in line:
                        break
                chunks.append("\n".join(body_lines))

        if not chunks:
            return split_into_chunks(lines)
        logger.info("Function parsing successful — found %d functions", len(chunks))
        return chunks

    except ParseError:
        logger.warning("Parse failed or no functions found, using fallback chunking")
        return split_into_chunks(lines)