import os
import requests
import numpy as np
from dotenv import load_dotenv

# 환경 변수 로드 (모듈 임포트 시 로드)
load_dotenv()
GMS_KEY = os.getenv("GMS_KEY")

EMBED_ENDPOINT = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/embeddings"
EMBED_MODEL = "text-embedding-3-large"

def get_embedding(text: str):
    """
    텍스트를 임베딩 벡터로 변환하는 함수.
    """
    if not GMS_KEY:
        print("[ERROR] GMS_KEY not found in environment variables.")
        return None

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GMS_KEY}"
    }

    body = {
        "model": EMBED_MODEL,
        "input": text
    }

    try:
        res = requests.post(EMBED_ENDPOINT, headers=headers, json=body)
        
        if res.status_code != 200:
            print("Embedding API Error:", res.status_code)
            with open("api_error.log", "w", encoding="utf-8") as f:
                f.write(res.text)
            return None

        return res.json()["data"][0]["embedding"]
    except Exception as e:
        print(f"[ERROR] Embedding request failed: {e}")
        return None

def get_average_embedding(vectors):
    """
    벡터 리스트의 평균 벡터를 계산하는 함수.
    vectors: list of lists (float)
    """
    if not vectors:
        return None
    
    try:
        # numpy를 사용하여 열(column) 단위 평균 계산
        avg_vector = np.mean(vectors, axis=0).tolist()
        return avg_vector
    except Exception as e:
        print(f"[ERROR] Failed to calculate average embedding: {e}")
        return None
