import requests

def analyze_text_with_ollama(text):
    url = "http://localhost:11434/api/generate"  # Ollama API 서버 URL
    headers = {"Content-Type": "application/json"}

    payload = {
        "model": "qwen2.5",  # 사용할 모델 이름
        "prompt": f"""
        너는 책의 일부를 분석해서 메타데이터를 추출하는 도우미야.
        아래 텍스트를 읽고, 아래 JSON 형식으로 응답해줘.

        텍스트:
        \"\"\"{text}\"\"\"

        JSON 응답:
        {{
          "local_genres": ["장르1", "장르2"],
          "local_tone": ["톤1", "톤2"],
          "local_style": ["문체1", "문체2"],
          "local_topics": ["주제1", "주제2"],
          "complexity_estimate": "난이도 예측값",
          "highlight_candidate": {{
            "reason": "하이라이트 이유",
            "excerpt": "하이라이트된 텍스트",
            "local_position_percent": 0.35
          }}
        }}
        """
    }

    # API 요청 보내기
    response = requests.post(url, headers=headers, json=payload)

    # 응답 텍스트 출력
    print("Response Text:")
    print(response.text)  # 응답 텍스트를 출력하여 확인

    # 응답을 JSON으로 변환
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

# 예시로 사용할 책 텍스트 청크 (텍스트 파일에서 가져오는 방식)
file_path = './toTag/sample.txt'  # 책의 텍스트 파일 경로

def read_text_from_file(file_path):
    """
    텍스트 파일을 읽어오는 함수
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# 책 텍스트를 읽어서 요약하기
book_text = read_text_from_file(file_path)
metadata = analyze_text_with_ollama(book_text)

if metadata:
    print(metadata)
