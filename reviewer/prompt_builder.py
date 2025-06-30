# prompt_builder.py

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

REVIEW_INSTRUCTION = (
    "Analyze the provided C code chunk below in the context of the listed guidelines. "
    "Flag any violations or issues. For each violation, include the line number, the matched guideline ID, and a brief suggestion. "
    "If no violations are found, return an empty list in the 'remarks' field. "
    "Response must strictly follow the JSON format shown."
)

OUTPUT_FORMAT_NOTE = """
{
  "remarks": [
    {
      "line": 12,
      "guideline_id": "G001",
      "issue": "Usage of ## operator detected",
      "suggestion": "Avoid using token-pasting macros for better readability."
    },
    ...
  ]
}
"""

def build_prompt(code_chunk: str, matched_guidelines: List[Dict]) -> str:
    """
    Assemble the final prompt string from the code chunk and relevant guidelines.
    """
    logger.debug("Building prompt for code chunk of %d characters", len(code_chunk))

    prompt_sections = []

    # Header: Relevant Guidelines
    prompt_sections.append("Relevant Guidelines:\n")
    for g in matched_guidelines:
        prompt_sections.append(f"- {g['id']} [{g['severity']} | {g['category']}]: {g['rule']}\n  {g['description']}\n")

    # Code Section (avoid triple backtick inside f-string)
    prompt_sections.append("\nCode to Review:\n")
    prompt_sections.append("```c\n")
    prompt_sections.append(code_chunk.strip())
    prompt_sections.append("\n```\n")

    # Review instruction
    prompt_sections.append("\nReview Instruction:\n")
    prompt_sections.append(REVIEW_INSTRUCTION)

    # Output format hint
    prompt_sections.append("\nOutput Format:\n")
    prompt_sections.append(OUTPUT_FORMAT_NOTE)

    final_prompt = "\n".join(prompt_sections)
    logger.info("Prompt built with %d guidelines and %d code characters", len(matched_guidelines), len(code_chunk))
    return final_prompt


def build_reference_trace_prompt(code_chunk: str) -> str:
    """
    Builds a second prompt that tells the AI agent to scan for file references in the code.
    """
    logger.debug("Building file reference trace prompt")

    output_format = """
{
  "name": "Potentially Impactful files to be reviewed later",
  "files": [
    {
      "fileName": "source/utils/print.h",
      "explanation": "Header file included in lineNumber 33"
    }
  ]
}
    """.strip()

    # Break f-string before adding ```c block to avoid unterminated error
    prompt_start = f"""
Analyze the following C code and identify any potentially referred file paths (e.g., via #include statements, or function calls declared in another module).
For each such reference, provide:
- fileName (relative or guessed path like "source/xyz.h" or "driver/uart.c")
- explanation: what was detected and the line number of occurrence.

If nothing found, return an empty list for "files".

Return strictly in the following JSON format:

{output_format}

Code to analyze:
"""

    # Append code block safely
    prompt_end = "```c\n" + code_chunk.strip() + "\n```"
    return prompt_start + prompt_end
