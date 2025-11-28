import os
import sys
import random
import json
import time
from dotenv import load_dotenv

# 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules import converter, splitter, tagger

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

    # 디렉토리 생성
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(txt_output_dir, exist_ok=True)
    os.makedirs(chunks_output_dir, exist_ok=True)
    os.makedirs(tags_output_dir, exist_ok=True)

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
        
        print(f"  [1/3] Converting to TXT: {txt_filename}")
        try:
            converter.convert_epub_to_txt(epub_path, txt_path)
        except Exception as e:
            print(f"  ❌ Failed to convert {epub_file}: {e}")
            continue

        # --- Step 2: TXT to Chunks ---
        print(f"  [2/3] Splitting into Chunks...")
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            chunks = splitter.split_into_chunks(text_content)
            
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
        print(f"  [3/3] Sampling and Tagging...")
        
        # 태그 저장 폴더: (원래제목)_tags
        book_tags_dir = os.path.join(tags_output_dir, f"{file_name_no_ext}_tags")
        os.makedirs(book_tags_dir, exist_ok=True)

        # 4개씩 그룹핑하여 랜덤 선택
        # chunks 리스트는 이미 메모리에 있음 (chunks 변수)
        # 하지만 파일 경로로 작업하는 것이 명확할 수 있으니 saved_chunk_paths 사용 가능
        # 여기서는 chunks 텍스트 데이터를 직접 사용
        
        selected_indices = []
        group_size = 4
        
        for i in range(0, len(chunks), group_size):
            group_indices = list(range(i, min(i + group_size, len(chunks))))
            if group_indices:
                selected_idx = random.choice(group_indices)
                selected_indices.append(selected_idx)
        
        print(f"    -> Selected {len(selected_indices)} chunks for tagging (out of {len(chunks)})")
        
        for i, idx in enumerate(selected_indices):
            chunk_text = chunks[idx]
            # 태그 파일명: (원래제목)_tag_01.json (순차 번호)
            tag_filename = f"{file_name_no_ext}_tag_{i+1:02d}.json"
            tag_path = os.path.join(book_tags_dir, tag_filename)
            
            print(f"    -> Tagging chunk {idx+1}/{len(chunks)} as {tag_filename}...", end="", flush=True)
            
            tags = tagger.tag_chunk_with_gpt(chunk_text)
            
            if tags:
                with open(tag_path, 'w', encoding='utf-8') as f:
                    json.dump(tags, f, ensure_ascii=False, indent=2)
                print(" Done.")
            else:
                print(" Failed.")
            
            # API Rate Limit 고려하여 잠시 대기 (선택사항)
            time.sleep(0.5)

    print("\n✅ All processing completed!")

if __name__ == "__main__":
    main()
