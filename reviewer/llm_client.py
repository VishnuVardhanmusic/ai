import json
import logging
from typing import Dict
import litellm
from prompt_builder import build_prompt, build_reference_trace_prompt

# Load from config
from config import MODEL_NAME, LITELLM_API_BASE, LITELLM_API_KEY

logger = logging.getLogger(__name__)

# LiteLLM settings
litellm.api_base = LITELLM_API_BASE
litellm.api_key = LITELLM_API_KEY


def _safe_parse_json(response_text: str) -> Dict:
    """
    Parses LLM response text to JSON safely.
    """
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error("❌ JSON parsing failed: %s", e)
        logger.debug("Raw LLM response:\n%s", response_text)
        return {}


def review_code_chunk(code_chunk: str, matched_guidelines: list) -> Dict:
    """
    Sends code + guideline match prompt to the LLM and returns the structured remarks JSON.
    """
    prompt = build_prompt(code_chunk, matched_guidelines)
    logger.info("Sending review prompt to LLM (length=%d chars)", len(prompt))

    try:
        response = litellm.completion(model=MODEL_NAME, messages=[
            {"role": "user", "content": prompt}
        ])
        content = response.choices[0].message.content
        parsed = _safe_parse_json(content)
        return parsed if isinstance(parsed, dict) else {"remarks": []}
    except Exception as e:
        logger.exception("❌ LLM review request failed")
        return {"remarks": []}


def trace_code_references(code_chunk: str) -> Dict:
    """
    Sends file-reference prompt to the LLM and returns the structured JSON of file links.
    """
    prompt = build_reference_trace_prompt(code_chunk)
    logger.info("Sending file reference prompt to LLM (length=%d chars)", len(prompt))

    try:
        response = litellm.completion(model=MODEL_NAME, messages=[
            {"role": "user", "content": prompt}
        ])
        content = response.choices[0].message.content
        parsed = _safe_parse_json(content)
        return parsed if isinstance(parsed, dict) else {"files": []}
    except Exception as e:
        logger.exception("❌ LLM file reference request failed")
        return {"files": []}


def analyze_chunk(code_chunk: str, matched_guidelines: list) -> Dict:
    """
    High-level function that combines both LLM prompts into a single result JSON.
    """
    logger.info("Analyzing one code chunk...")
    result = {
        "remarks": review_code_chunk(code_chunk, matched_guidelines).get("remarks", []),
        "related_files": trace_code_references(code_chunk)
    }
    logger.info("Analysis complete: %d remarks, %d related files",
                len(result["remarks"]), len(result["related_files"].get("files", [])))
    return result
