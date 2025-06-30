# rag_engine.py

import json
import os
import logging
from typing import List, Tuple
from sentence_transformers import SentenceTransformer, util
from config import GUIDELINE_JSON_PATH, MAX_GUIDELINE_MATCHES

logger = logging.getLogger(__name__)

# Load sentence transformer model once
logger.info("Loading sentence-transformer model (all-MiniLM-L6-v2)...")
model = SentenceTransformer("all-MiniLM-L6-v2")
logger.info("Model loaded successfully")


def load_guidelines(guideline_path: str) -> List[dict]:
    with open(guideline_path, "r") as f:
        data = json.load(f)
    logger.info("Loaded %d guidelines from %s", len(data), guideline_path)
    return data


def embed_guidelines(guidelines: List[dict]) -> Tuple[List[dict], List[List[float]]]:
    texts = [f"{g['rule']}. {g['description']}" for g in guidelines]
    logger.info("Generating embeddings for %d guidelines", len(texts))
    embeddings = model.encode(texts, convert_to_tensor=True)
    return guidelines, embeddings


def retrieve_top_matches(code_chunk: str, guideline_data: List[dict], guideline_embeddings, top_k=MAX_GUIDELINE_MATCHES) -> List[dict]:
    query = model.encode(code_chunk, convert_to_tensor=True)
    logger.debug("Embedding code chunk of %d characters", len(code_chunk))

    scores = util.cos_sim(query, guideline_embeddings)[0]
    top_results = scores.topk(top_k)

    matches = []
    for idx, score in zip(top_results.indices, top_results.values):
        guideline = guideline_data[idx]
        guideline_copy = guideline.copy()
        guideline_copy["match_score"] = float(score)
        matches.append(guideline_copy)

    logger.info("Matched top %d guidelines (min score: %.4f)", top_k, float(top_results.values[-1]))
    return matches
