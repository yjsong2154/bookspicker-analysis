import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
GMS_KEY = os.getenv("GMS_KEY")

ANALYSIS_SYSTEM_PROMPT = """
당신은 소설/논픽션 텍스트를 분석해 메타데이터를 추출하는 태깅 엔진입니다.
사용자가 준 본문(청크)만 보고, 외부 지식(웹 검색, 줄거리 기억 등)은 사용하지 마세요.
알 수 없는 정보는 추측하지 말고 null 또는 적절한 기본값을 사용하세요.

아래 스키마를 따르는 하나의 JSON 객체만 출력하세요.
설명 문장, 마크다운, 코드블록, 주석은 절대 넣지 마세요. JSON만 출력하세요.

필드 스키마와 값 규칙:

{
  "is_fiction": "fiction | non_fiction | mixed | null",

  "primary_genres": ["상위 장르들 (예: '판타지', '로맨스', '미스터리', 'SF', '에세이', '자기계발', '인문', '경제경영' 등)"],
  "subgenres": ["세부 장르 태그들 (예: '로맨스 판타지', '심리 스릴러', '성장소설' 등)"],
  "main_topics": ["주요 소재·주제 태그들 (예: '성장', '우정', '복수', '전쟁', '직장생활', '연애', '가족', '우울', '삶의 의미' 등)"],

  "length_category": "short_story | novella | novel | epic | short_form | standard | long_form | null",
  "is_series": "standalone | series_first | series_middle | series_last | null",
  "structure_features": ["구조 특징 (예: '짧은 에피소드 형식', '연속된 서사', '일기 형식', '편지 형식', '옴니버스' 등)"],

  "narrative_pov": "first_person | third_limited | third_omniscient | multi_pov | other | null",
  "tense": "past | present | mixed | null",
  "style_descriptors": ["문체 특징 (예: '간결한', '묘사가 풍부한', '시적인', '직설적인', '유머러스한', '철학적인', '감정선이 섬세한', '대사가 많은', '설명이 많은' 등)"],
  "tone_mood": ["전체 분위기/정서 (예: '어두운', '따뜻한', '희망적인', '우울한', '잔잔한', '긴장감 있는', '잔혹한', '로맨틱한', '우스운' 등)"],
  "complexity_level": "easy | normal | challenging | very_challenging | null",

  "character_vs_plot_driven": "character_driven | plot_driven | balanced | idea_driven | null",
  "emotional_impact": ["감정 태그 (예: '감동', '카타르시스', '슬픔', '몰입감', '위로', '여운', '공포' 등)"],
  "reading_energy": "light | moderate | heavy | null",
  "target_audience": "children | YA | adult | all_age | null",

  "world_type": "realistic_modern | historical | secondary_fantasy_world | sci_fi_setting | alternate_history | abstract | other | null",
  "time_period": "contemporary | 19th_century | medieval_like | future | modern_history | unspecified | null",
  "primary_locales": ["주요 무대 (예: '도시', '시골', '학교', '회사', '우주선', '전장', '가정', '여행지' 등)"],

  "nonfiction_type": "essay | self_help | history | science | psychology | business | philosophy | other | null",
  "main_subjects": ["비소설일 때 주요 학문·주제 (예: '행동경제학', '인지심리학', '한국 현대사', '스타트업', '리더십' 등)"],
  "practicality_level": "highly_practical | mixed | theoretical | null",
  "depth_level": "introductory | intermediate | advanced | null",

  "content_warnings": {
    "violence": "none | mild | moderate | severe",
    "sexual_content": "none | mild | moderate | explicit",
    "abuse": "none | mild | moderate | severe",
    "self_harm": "none | mild | moderate | severe",
    "drug_use": "none | mild | moderate | severe",
    "discrimination": "none | mild | moderate | severe"
  },
  "age_rating_estimate": "all | 12+ | 15+ | 19+ | unknown"
}

조건:
- 각 배열은 0~5개 정도로 짧게 유지하세요.
- 본문만으로 확실하지 않으면 공격적으로 추측하지 말고 null, "unknown", 또는 빈 배열을 사용하세요.
- content_warnings 필드는 항상 위의 키들을 모두 포함해야 합니다.
"""

def tag_chunk_with_gpt(chunk: str) -> dict | None:
    """
    책 본문 청크(text)를 입력으로 받아, 분석 스키마에 맞는 태그 JSON(dict)을 반환.
    오류가 나면 None 반환.
    """
    gms_key = GMS_KEY

    gpt_endpoint = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {gms_key}",
    }

    user_prompt = f"""
다음은 책의 일부(청크)입니다. 이 텍스트만 보고 위 스키마에 맞는 JSON을 생성하세요.

[텍스트 시작]
{chunk}
[텍스트 끝]
"""

    body = {
        "model": "gpt-5-nano",
        "messages": [
            {"role": "developer", "content": ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    }

    try:
        res = requests.post(gpt_endpoint, headers=headers, json=body)
        
        if res.status_code != 200:
            print("API Error:", res.status_code, res.text)
            return None

        content = res.json()["choices"][0]["message"]["content"].strip()
        
        # LLM이 JSON만 반환했다고 가정하고 파싱
        try:
            parsed = json.loads(content)
            return parsed
        except json.JSONDecodeError:
            # 혹시 모를 앞뒤 텍스트/코드블록 제거용 간단한 fallback
            try:
                if "{" in content and "}" in content:
                    json_str = content[content.index("{"): content.rindex("}") + 1]
                    return json.loads(json_str)
            except Exception:
                pass

            print("JSON 파싱 실패. 원본 응답:")
            print(content)
            return None
            
    except Exception as e:
        print(f"Request failed: {e}")
        return None
