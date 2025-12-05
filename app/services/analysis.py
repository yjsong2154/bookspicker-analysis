import os
import time
import json
import random
import shutil
import uuid
from typing import Dict, Any, List
from .modules import converter, splitter, tagger, aggregator, vectorizer

# Temp directory for processing
TEMP_DIR = "storage/temp"
os.makedirs(TEMP_DIR, exist_ok=True)

def analyze_epub(file_path: str) -> Dict[str, Any]:
    """
    Analyzes an EPUB file and returns metadata, tags, and embedding.
    """
    start_time = time.time()
    print(f"🚀 Starting analysis for: {file_path}")

    session_id = str(uuid.uuid4())
    session_dir = os.path.join(TEMP_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    try:
        # 1. Convert EPUB to TXT
        step_start = time.time()
        print("  [1/5] Converting EPUB to TXT...", end="", flush=True)
        txt_filename = "content.txt"
        txt_path = os.path.join(session_dir, txt_filename)
        
        converter.convert_epub_to_txt(file_path, txt_path)
        
        with open(txt_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
        print(f" Done ({time.time() - step_start:.2f}s)")

        # 2. Split into Chunks (for Tagging)
        step_start = time.time()
        print("  [2/5] Splitting text into chunks...", end="", flush=True)
        chunks = splitter.split_into_chunks(text_content)
        print(f" Done ({len(chunks)} chunks, {time.time() - step_start:.2f}s)")
        
        # 3. Sampling & Tagging
        step_start = time.time()
        print("  [3/5] Sampling and Tagging...", flush=True)
        target_sample_count = 5
        selected_indices = _sample_indices(len(chunks), target_sample_count)
        
        tag_results = []
        for i, idx in enumerate(selected_indices):
            print(f"    - Processing chunk {i+1}/{len(selected_indices)}...", end="", flush=True)
            chunk_text = chunks[idx]
            tags = tagger.tag_chunk_with_gpt(chunk_text)
            if tags:
                tag_results.append(tags)
            print(" Done")
        print(f"    > Tagging complete ({time.time() - step_start:.2f}s)")
        
        # 4. Aggregate Tags
        step_start = time.time()
        print("  [4/5] Aggregating tags...", end="", flush=True)
        tags_dir = os.path.join(session_dir, "tags")
        os.makedirs(tags_dir, exist_ok=True)
        
        for i, tags in enumerate(tag_results):
            with open(os.path.join(tags_dir, f"chunk_tag_{i:02d}.json"), 'w', encoding='utf-8') as f:
                json.dump(tags, f, ensure_ascii=False)
                
        # Use aggregator module
        agg_output_dir = os.path.join(session_dir, "aggregated")
        aggregator.aggregate_tags(tags_dir, agg_output_dir, "book")
        
        final_tags_path = os.path.join(agg_output_dir, "book_tag_all.json")
        final_tags = {}
        if os.path.exists(final_tags_path):
            with open(final_tags_path, 'r', encoding='utf-8') as f:
                final_tags = json.load(f)
        print(f" Done ({time.time() - step_start:.2f}s)")

        # 5. Vector Processing
        step_start = time.time()
        print("  [5/5] Generating vectors...", flush=True)
        # Re-split for vectors (chunk_size=500)
        vec_chunks = splitter.split_into_chunks(text_content, chunk_size=500)
        vec_selected_indices = _sample_indices(len(vec_chunks), target_sample_count)
        
        generated_vectors = []
        for i, idx in enumerate(vec_selected_indices):
            print(f"    - Vectorizing chunk {i+1}/{len(vec_selected_indices)}...", end="", flush=True)
            chunk_text = vec_chunks[idx]
            vector = vectorizer.get_embedding(chunk_text)
            if vector:
                generated_vectors.append(vector)
            print(" Done")
        
        avg_vector = vectorizer.get_average_embedding(generated_vectors)
        print(f"    > Vectorization complete ({time.time() - step_start:.2f}s)")
        
        total_time = time.time() - start_time
        print(f"✅ Analysis finished successfully in {total_time:.2f}s")

        return {
            "tags": final_tags,
            "embedding": avg_vector
        }

    finally:
        # Cleanup
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)

def _sample_indices(total_length: int, sample_count: int) -> List[int]:
    if total_length <= sample_count:
        return list(range(total_length))
    
    indices = []
    segment_size = total_length / sample_count
    for i in range(sample_count):
        start_idx = int(i * segment_size)
        end_idx = int((i + 1) * segment_size)
        if i == sample_count - 1:
            end_idx = total_length
        
        if start_idx < end_idx:
            selected_idx = random.randint(start_idx, end_idx - 1)
            indices.append(selected_idx)
    return indices
