import os
import requests
from dotenv import load_dotenv

load_dotenv()
GMS_KEY = os.getenv("GMS_KEY")

# -------------------------
# 1. 텍스트 파일 읽기
# -------------------------
def load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# # -------------------------
# # 2. 청크 나누기
# # -------------------------
# def split_into_chunks(text, chunk_size=2000, overlap=200):
#     """
#     chunk_size: 청크의 최대 길이
#     overlap: 앞뒤 문맥을 유지하기 위해 겹치는 길이
#     """
#     chunks = []
#     start = 0
#     length = len(text)

#     while start < length:
#         end = min(start + chunk_size, length)
#         chunk = text[start:end]
#         chunks.append(chunk)
#         start += (chunk_size - overlap)

#     return chunks


# -------------------------
# 3. GPT API 호출 함수
# -------------------------
def summarize_chunk(chunk):
    url = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GMS_KEY}"
    }

    data = {
        "model": "gpt-5-mini",
        "messages": [
            {"role": "developer", "content": "Answer in Korean"},
            {
                "role": "user",
                "content": f"""
다음 텍스트를 한국어로 간결히 요약해줘:

\"\"\"{chunk}\"\"\"
"""
            }
        ]
    }

    res = requests.post(url, headers=headers, json=data)

    if res.status_code != 200:
        print("API Error:", res.status_code, res.text)
        return None

    result = res.json()
    return result["choices"][0]["message"]["content"]


# -------------------------
# 4. 전체 파이프라인 실행
# -------------------------
if __name__ == "__main__":
    file_path = "./toTag/sample.txt"
    text = load_text(file_path)

    # chunks = split_into_chunks(text)
    # print(f"총 청크 개수: {len(chunks)}")

    # summaries = []

    # for i, chunk in enumerate(chunks):
    #     print(f"\n=== 청크 {i+1}/{len(chunks)} 요약 중... ===")
    #     summary = summarize_chunk(chunk)
    #     summaries.append(summary)
    #     print(summary)

    summary = summarize_chunk(text)
    print(summary)

    # 최종 파일 저장
    with open("./toTag/summary_result.txt", "w", encoding="utf-8") as f:
        f.write(f"{summary}")

    print("\n요약 완료! summary_result.txt 파일을 확인하세요.")
