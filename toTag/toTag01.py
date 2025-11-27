import os
import requests
from dotenv import load_dotenv
import tiktoken

load_dotenv()
GMS_KEY = os.getenv("GMS_KEY")

# -------------------------
# 토큰 계산 함수
# -------------------------
def count_tokens(text: str, model: str = "gpt-4o-mini"):
    """
    cl100k_base 토크나이저로 토큰 수 추정
    실제 GPT-5 계열과 약간 차이날 수는 있지만 근사치는 매우 정확함
    """
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def estimate_request_tokens(chunk: str, max_output_tokens: int = 150) -> int:
    """
    API 호출 전 전체 토큰 수를 미리 계산하는 함수
    """

    # 프롬프트 텍스트
    prompt_text = f"""
다음 텍스트를 한국어로 간결히 요약해줘:

\"\"\"{chunk}\"\"\"
"""

    # messages 토큰 계산
    developer_msg = "Answer in Korean"
    developer_tokens = count_tokens(developer_msg)

    user_tokens = count_tokens(prompt_text)

    total_input_tokens = developer_tokens + user_tokens

    # 총 예상 토큰 = 입력 + 출력(max_tokens)
    total_estimated_tokens = total_input_tokens*0.0005 + max_output_tokens*0.004

    print("----- 토큰 예상 -----")
    print(f"입력 토큰(프롬프트+청크): {total_input_tokens} 토큰 , {total_input_tokens*0.0005}")
    print(f"출력 토큰 예상(max={max_output_tokens}): {max_output_tokens*0.004}")
    print(f"총 토큰 예상: {total_estimated_tokens}")
    print("---------------------")

    return total_estimated_tokens


# -------------------------
# 1. 텍스트 파일 읽기
# -------------------------
def load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# -------------------------
# 2. GPT API 호출
# -------------------------
def summarize_chunk(chunk):
    url = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GMS_KEY}"
    }

    data = {
        "model": "gpt-5-nano",
        # "max_completion_tokens": 1000,  # 출력 제한
        "messages": [
            {"role": "developer", "content": "Answer in Korean"},
            {"role": "user", "content": f"아래 텍스트를 한국어로 1000자 이내로 요약:\n\n{chunk}"}
        ]
    }

    # API 요청
    res = requests.post(url, headers=headers, json=data)

    if res.status_code != 200:
        print("API Error:", res.status_code, res.text)
        return None

    result = res.json() 
    print(result)
    return result["choices"][0]["message"]["content"]


# -------------------------
# 3. 실행부
# -------------------------
if __name__ == "__main__":
    file_path = "./toTag/book.txt"
    text = load_text(file_path)

    # API 호출 전에 토큰 먼저 계산하기
    estimate_request_tokens(text, max_output_tokens=1000)

    # 실제 API 호출
    summary = summarize_chunk(text)
    print("\n=== 요약 결과 ===")
    print(summary)

    with open("./toTag/book01.txt", "w", encoding="utf-8") as f:
        f.write(summary)

    # print("\n요약 완료! book01.txt 파일을 확인하세요.")
