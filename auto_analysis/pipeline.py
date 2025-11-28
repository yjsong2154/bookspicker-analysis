import os
import sys
import random
import json
import time
from dotenv import load_dotenv

# 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules import converter, splitter, tagger, aggregator, vectorizer

def main():
    # 1. 환경 설정
    load_dotenv() # .env 파일 로드 (현재 디렉토리 또는 상위 디렉토리 탐색)
    
    if not os.getenv("GMS_KEY"):
        print("⚠️  Warning: GMS_KEY not found in environment variables. Tagging might fail.")
        print("Please ensure .env file exists in this directory or parent directory.")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "input")
    output_dir = os.path.join(base_dir, "output")
    
    txt_output_dir = os.path.join(output_dir, "txt")
    chunks_output_dir = os.path.join(output_dir, "chunks")
    tags_output_dir = os.path.join(output_dir, "tags")
    final_tags_output_dir = os.path.join(output_dir, "final_tags") # 최종 태그 저장 폴더
    
    # 벡터 관련 폴더
    chunks_vec_output_dir = os.path.join(output_dir, "chunks_vec")
    vecs_output_dir = os.path.join(output_dir, "vecs")
    final_vec_output_dir = os.path.join(output_dir, "final_vec")

    # 디렉토리 생성
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(txt_output_dir, exist_ok=True)
    os.makedirs(chunks_output_dir, exist_ok=True)
    os.makedirs(tags_output_dir, exist_ok=True)
    os.makedirs(final_tags_output_dir, exist_ok=True)
    os.makedirs(chunks_vec_output_dir, exist_ok=True)
    os.makedirs(vecs_output_dir, exist_ok=True)
    os.makedirs(final_vec_output_dir, exist_ok=True)

    # 2. EPUB 파일 목록 스캔
    epub_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.epub')]
    
    if not epub_files:
        print(f"ℹ️  No .epub files found in {input_dir}")
        print("Please place .epub files in the 'input' directory and run again.")
        return

    print(f"📚 Found {len(epub_files)} epub files. Starting processing...")

    for epub_file in epub_files:
        print(f"\n🚀 Processing: {epub_file}")
        file_name_no_ext = os.path.splitext(epub_file)[0]
        epub_path = os.path.join(input_dir, epub_file)
        
        # --- Step 1: EPUB to TXT ---
        txt_filename = f"{file_name_no_ext}_text.txt"
        txt_path = os.path.join(txt_output_dir, txt_filename)
        
        print(f"  [1/5] Converting to TXT: {txt_filename}")
        try:
            converter.convert_epub_to_txt(epub_path, txt_path)
        except Exception as e:
            print(f"  ❌ Failed to convert {epub_file}: {e}")
            continue

        # --- Step 2: TXT to Chunks (Tagging용) ---
        print(f"  [2/5] Splitting into Chunks (for Tagging)...")
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            chunks = splitter.split_into_chunks(text_content) # 기본 설정 사용
            
            # 청크 저장 폴더: (원래제목)_chunks
            book_chunks_dir = os.path.join(chunks_output_dir, f"{file_name_no_ext}_chunks")
            # 파일 prefix: (원래제목)_chunk
            chunk_prefix = f"{file_name_no_ext}_chunk"
            
            saved_chunk_paths = splitter.save_chunks(chunks, book_chunks_dir, chunk_prefix)
            print(f"    -> Created {len(saved_chunk_paths)} chunks in {book_chunks_dir}")
            
        except Exception as e:
            print(f"  ❌ Failed to split chunks for {epub_file}: {e}")
            continue

        # --- Step 3: Sampling & Tagging ---
        print(f"  [3/5] Sampling and Tagging...")
        
        # 태그 저장 폴더: (원래제목)_tags
        book_tags_dir = os.path.join(tags_output_dir, f"{file_name_no_ext}_tags")
        os.makedirs(book_tags_dir, exist_ok=True)

        # 전체 청크 중 5개를 균일하게 랜덤 선택
        target_sample_count = 5
        selected_indices = []
        
        if len(chunks) <= target_sample_count:
            selected_indices = list(range(len(chunks)))
        else:
            # 전체를 5개 구간으로 나누어 각 구간에서 하나씩 선택
            segment_size = len(chunks) / target_sample_count
            for i in range(target_sample_count):
                start_idx = int(i * segment_size)
                end_idx = int((i + 1) * segment_size)
                
                if i == target_sample_count - 1:
                    end_idx = len(chunks)
                
                if start_idx < end_idx:
                    selected_idx = random.randint(start_idx, end_idx - 1)
                    selected_indices.append(selected_idx)
        
        print(f"    -> Selected {len(selected_indices)} chunks for tagging (out of {len(chunks)})")
        
        for i, idx in enumerate(selected_indices):
            chunk_text = chunks[idx]
            tag_filename = f"{file_name_no_ext}_tag_{i+1:02d}.json"
            tag_path = os.path.join(book_tags_dir, tag_filename)
            
            if os.path.exists(tag_path):
                 print(f"    -> Tagging chunk {idx+1}/{len(chunks)} as {tag_filename}... (Skipping, file exists)")
                 continue

            print(f"    -> Tagging chunk {idx+1}/{len(chunks)} as {tag_filename}...", end="", flush=True)
            
            tags = tagger.tag_chunk_with_gpt(chunk_text)
            
            if tags:
                with open(tag_path, 'w', encoding='utf-8') as f:
                    json.dump(tags, f, ensure_ascii=False, indent=2)
                print(" Done.")
            else:
                print(" Failed.")
            
            time.sleep(0.5)

        # --- Step 4: Tag Aggregation ---
        print(f"  [4/5] Aggregating Tags...")
        try:
            aggregator.aggregate_tags(book_tags_dir, final_tags_output_dir, file_name_no_ext)
        except Exception as e:
            print(f"  ❌ Failed to aggregate tags: {e}")

        # --- Step 5: Vector Processing ---
        print(f"  [5/5] Processing Vectors...")
        try:

            # 1) 텍스트 재분할 (Vector용, chunk_size=500)
            # Note: 1600 words exceeded 8192 token limit (approx 12k tokens). 
            # Adjusted to 500 words (~4k tokens) to be safe.
            print("    -> Re-splitting text for vectors (chunk_size=500)...")
            vec_chunks = splitter.split_into_chunks(text_content, chunk_size=500)
            
            # 벡터 청크 저장 (선택 사항이지만 요청에 포함됨)
            book_vec_chunks_dir = os.path.join(chunks_vec_output_dir, f"{file_name_no_ext}_vec_chunks")
            vec_chunk_prefix = f"{file_name_no_ext}_vec_chunk"
            splitter.save_chunks(vec_chunks, book_vec_chunks_dir, vec_chunk_prefix)
            print(f"    -> Created {len(vec_chunks)} vector chunks in {book_vec_chunks_dir}")

            # 2) 샘플링 (5개 균일)
            vec_selected_indices = []
            if len(vec_chunks) <= target_sample_count:
                vec_selected_indices = list(range(len(vec_chunks)))
            else:
                segment_size = len(vec_chunks) / target_sample_count
                for i in range(target_sample_count):
                    start_idx = int(i * segment_size)
                    end_idx = int((i + 1) * segment_size)
                    if i == target_sample_count - 1:
                        end_idx = len(vec_chunks)
                    if start_idx < end_idx:
                        selected_idx = random.randint(start_idx, end_idx - 1)
                        vec_selected_indices.append(selected_idx)
            
            print(f"    -> Selected {len(vec_selected_indices)} chunks for vectorization")

            # 3) 벡터 생성 및 저장
            generated_vectors = []
            book_vecs_dir = os.path.join(vecs_output_dir, f"{file_name_no_ext}_vecs")
            os.makedirs(book_vecs_dir, exist_ok=True)

            for i, idx in enumerate(vec_selected_indices):
                chunk_text = vec_chunks[idx]
                vec_filename = f"{file_name_no_ext}_vec_{i+1:02d}.json"
                vec_path = os.path.join(book_vecs_dir, vec_filename)

                print(f"    -> Vectorizing chunk {idx+1}/{len(vec_chunks)}...", end="", flush=True)
                
                # 이미 존재하면 로드 (API 절약)
                if os.path.exists(vec_path):
                    print(" (Loading existing)...", end="")
                    with open(vec_path, 'r', encoding='utf-8') as f:
                        vector = json.load(f)
                else:
                    vector = vectorizer.get_embedding(chunk_text)
                    if vector:
                        with open(vec_path, 'w', encoding='utf-8') as f:
                            json.dump(vector, f)
                
                if vector:
                    generated_vectors.append(vector)
                    print(" Done.")
                else:
                    print(" Failed.")
                
                time.sleep(0.2) # Rate limit

            # 4) 평균 벡터 계산 및 저장
            if generated_vectors:
                avg_vector = vectorizer.get_average_embedding(generated_vectors)
                if avg_vector:
                    final_vec_filename = f"{file_name_no_ext}_vec_all.json"
                    final_vec_path = os.path.join(final_vec_output_dir, final_vec_filename)
                    
                    with open(final_vec_path, 'w', encoding='utf-8') as f:
                        json.dump(avg_vector, f)
                    print(f"    -> Final average vector saved to {final_vec_path}")
                else:
                    print("    ❌ Failed to calculate average vector.")
            else:
                print("    ❌ No vectors generated.")

        except Exception as e:
            print(f"  ❌ Failed to process vectors: {e}")

    print("\n✅ All processing completed!")

if __name__ == "__main__":
    main()
