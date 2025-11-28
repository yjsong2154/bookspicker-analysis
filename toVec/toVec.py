import os
import requests
from dotenv import load_dotenv

load_dotenv()
GMS_KEY = os.getenv("GMS_KEY")

EMBED_ENDPOINT = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/embeddings"
EMBED_MODEL = "text-embedding-3-large"


def load_text_from_file(path: str) -> str:
    """
    txt 파일을 읽어서 문자열로 반환하는 함수.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"[ERROR] 파일을 찾을 수 없습니다: {path}")
        return None
    except UnicodeDecodeError:
        print(f"[ERROR] 파일 인코딩 오류: {path} (utf-8로 다시 저장 필요)")
        return None


def get_embedding(text: str):
    """
    텍스트를 임베딩 벡터로 변환하는 함수.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GMS_KEY}"
    }

    body = {
        "model": EMBED_MODEL,
        "input": text
    }

    res = requests.post(EMBED_ENDPOINT, headers=headers, json=body)

    if res.status_code != 200:
        print("Embedding API Error:", res.status_code, res.text)
        return None

    return res.json()["data"][0]["embedding"]


if __name__ == "__main__":
    # 👉 디렉토리 설정
    book_dir = "./toVec/book"
    output_dir = "./toVec/output"

    # 디렉토리가 없으면 생성 (혹시 모를 에러 방지)
    os.makedirs(book_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # book 폴더 내의 모든 txt 파일 찾기
    files = [f for f in os.listdir(book_dir) if f.endswith(".txt")]

    if not files:
        print(f"'{book_dir}' 폴더에 .txt 파일이 없습니다.")
        exit()

    print(f"총 {len(files)}개의 파일을 처리합니다: {files}\n")

    for filename in files:
        file_path = os.path.join(book_dir, filename)
        
        # 1) 파일 읽기
        print(f"Processing: {filename}...")
        text = load_text_from_file(file_path)
        if text is None:
            continue

        # 2) 임베딩 생성
        vector = get_embedding(text)

        if vector is not None:
            # 3) 저장하기
            # 확장자(.txt)를 제거하고 _vec.json 붙이기
            name_without_ext = os.path.splitext(filename)[0]
            output_filename = f"{name_without_ext}_vec.json"
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                # JSON 형식으로 저장 (리스트 형태 그대로)
                import json
                json.dump(vector, f)

            print(f" -> Saved to {output_path}")
        else:
            print(f" -> Failed to generate embedding for {filename}")
        
        print("-" * 30)

    print("\n모든 작업이 완료되었습니다.")
