import argparse
import os
import glob
import json
import logging
from code_loader import readCodeFile
from prompt_manager import buildPrompt
from review_engine import runParallelReviews, saveReviewToFile

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="🔹 [%(levelname)s] %(message)s"
)

def main():
    parser = argparse.ArgumentParser(description="🔍 Embedded C Code Reviewer (Parallel Multi-Agent)")
    parser.add_argument("filepath", help="Path to input .c or .h file")
    parser.add_argument(
        "--guidelines_dir",
        default="knowledge_base/",
        help="Directory containing g1.json to g5.json guideline chunks"
    )
    parser.add_argument(
        "--model",
        default="ollama/llama3",
        help="Model name as configured in litellm_config.yaml"
    )
    parser.add_argument(
        "--output",
        default="code_review.json",
        help="Path to save merged JSON review result"
    )
    args = parser.parse_args()

    try:
        logging.info("Reading source code from file: %s", args.filepath)
        code_lines = readCodeFile(args.filepath)

        logging.info("Loading guideline chunks from: %s", args.guidelines_dir)
        chunk_paths = sorted(glob.glob(os.path.join(args.guidelines_dir, "g*.json")))
        if not chunk_paths:
            raise FileNotFoundError("No guideline chunk files (g*.json) found in specified directory.")

        all_guideline_chunks = []
        for path in chunk_paths:
            with open(path, "r") as f:
                chunk = json.load(f)
                all_guideline_chunks.append(chunk)
                logging.info("Loaded %d rules from %s", len(chunk), os.path.basename(path))

        logging.info("Running %d parallel AI agents using model: %s", len(all_guideline_chunks), args.model)
        final_review = runParallelReviews(code_lines, all_guideline_chunks, model=args.model)

        logging.info("Saving merged review results to: %s", args.output)
        saveReviewToFile(final_review, args.output)

        logging.info("✅ Review process completed successfully.")

    except Exception as e:
        logging.error("❌ Review process failed: %s", str(e))

if __name__ == "__main__":
    main()
