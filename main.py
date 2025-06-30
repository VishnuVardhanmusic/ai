import os
import json
import logging
import sys
from reviewer.rag_engine import load_guidelines, embed_guidelines, retrieve_top_matches
from code_parser.chunker import extract_function_chunks
from reviewer.llm_client import analyze_chunk
from reviewer.html_generator import html_gen

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

GUIDELINE_FILE = "guidelines/guidelines.json"
OUTPUT_FILE = "outputs/review.json"

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_code_file.c/.h>")
        sys.exit(1)

    code_path = sys.argv[1]
    if not os.path.isfile(code_path):
        print(f"Error: File not found - {code_path}")
        sys.exit(1)

    logging.info(f"🚀 Starting review for file: {code_path}")

    # Step 1: Load and embed guidelines
    logging.info("📘 Loading guidelines...")
    guidelines, embeddings = embed_guidelines(load_guidelines(GUIDELINE_FILE))

    # Step 2: Chunk code
    logging.info("🧩 Chunking input code...")
    code_chunks = extract_function_chunks(code_path)

    if not code_chunks:
        logging.warning("⚠️ No chunks found. Possibly empty or unparseable file.")
        sys.exit(1)

    # Step 3: Analyze each chunk
    full_results = []
    total_remarks = 0
    total_refs = 0

    for idx, chunk in enumerate(code_chunks):
        logging.info(f"\n🔍 Reviewing Chunk {idx+1}/{len(code_chunks)}...")
        matched = retrieve_top_matches(chunk, guidelines, embeddings)
        result = analyze_chunk(chunk, matched)
        full_results.append(result)
        total_remarks += len(result.get("remarks", []))
        total_refs += len(result.get("related_files", {}).get("files", []))

    # Step 4: Write output
    logging.info(f"\n📝 Writing review to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(full_results, f, indent=2)

    # Step 5: Summary
    print("\n✅ Review Complete")
    print(f"📄 Chunks Reviewed: {len(code_chunks)}")
    print(f"⚠️  Total Remarks Found: {total_remarks}")
    print(f"📂 Referenced Files Detected: {total_refs}")
    print(f"📁 Output JSON Saved To: {OUTPUT_FILE}")
    html_gen(OUTPUT_FILE)
    

if __name__ == "__main__":
    main()
