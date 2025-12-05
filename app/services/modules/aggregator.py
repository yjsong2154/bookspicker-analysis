import os
import json
from collections import defaultdict

def recursive_merge(summary, data):
    """
    재귀적으로 딕셔너리를 순회하며 카운트를 집계합니다.
    summary: 집계 결과를 저장할 딕셔너리 (defaultdict 구조)
    data: 현재 처리 중인 데이터 (dict, list, str, etc.)
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key not in summary:
                # 키가 없으면 새로운 defaultdict 생성 (재귀를 위해)
                # 값이 dict가 아니면 카운팅을 위한 defaultdict(int)
                # 값이 dict면 다시 구조를 잡아야 함.
                # 단순하게 가기 위해, summary[key]를 재귀 호출
                if isinstance(value, dict):
                    summary[key] = summary.get(key, {})
                else:
                    summary[key] = summary.get(key, defaultdict(int))
            
            # 재귀 호출 또는 카운팅
            if isinstance(value, dict):
                recursive_merge(summary[key], value)
            elif isinstance(value, list):
                # 리스트인 경우 각 항목 카운트
                for item in value:
                    summary[key][item] += 1
            else:
                # 문자열/숫자 등 단일 값인 경우 해당 값 카운트
                summary[key][value] += 1

    elif isinstance(data, list):
        # 최상위가 리스트인 경우는 잘 없지만 처리 (단순 리스트 병합은 아님, 여기선 구조상 dict 안의 list로 처리됨)
        pass

def aggregate_tags(tag_dir, output_dir, file_prefix):
    """
    tag_dir 내의 부분 태그 파일들을 읽어 통합된 카운트 정보를 output_dir에 저장합니다.
    """
    print(f"    -> Aggregating tags from {tag_dir}...")
    
    # 1. 파일 목록 수집
    tag_files = [f for f in os.listdir(tag_dir) if f.endswith(".json") and "_tag_" in f and not f.endswith("_tag_all.json")]
    
    if not tag_files:
        print("    -> No tag files found to aggregate.")
        return

    # 2. 데이터 집계
    # 구조: { "field_name": { "value1": count, "value2": count }, "nested_field": { "sub_field": { "value": count } } }
    aggregated_data = {}

    for tag_file in tag_files:
        file_path = os.path.join(tag_dir, tag_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 재귀적으로 데이터 병합
            # aggregated_data는 동적으로 구조가 잡혀야 함.
            # 편의상 직접 구현보다는, 위에서 정의한 recursive_merge 사용
            # 하지만 defaultdict와 dict가 섞이면 나중에 json dump할 때 문제될 수 있음.
            # 따라서 dict로 변환하는 과정이 필요하거나, 처음부터 dict로 관리.
            
            # 간단한 구현:
            for key, value in data.items():
                if key not in aggregated_data:
                    aggregated_data[key] = defaultdict(int)
                
                if isinstance(value, list):
                    for item in value:
                        aggregated_data[key][item] += 1
                elif isinstance(value, dict):
                    # 중첩 딕셔너리 (예: content_warnings)
                    # 구조를 { "content_warnings": { "violence": { "moderate": 1 } } } 형태로 변경
                    if not isinstance(aggregated_data[key], dict):
                        aggregated_data[key] = {} # defaultdict(int) 였던 것을 덮어씀 (첫 발견시)
                    
                    for sub_key, sub_value in value.items():
                        if sub_key not in aggregated_data[key]:
                            aggregated_data[key][sub_key] = defaultdict(int)
                        aggregated_data[key][sub_key][sub_value] += 1
                else:
                    # 문자열/숫자 등
                    aggregated_data[key][value] += 1

        except Exception as e:
            print(f"    [WARNING] Failed to process {tag_file}: {e}")

    # 3. defaultdict를 일반 dict로 변환 (JSON 직렬화 위해)
    final_data = {}
    for key, value in aggregated_data.items():
        if isinstance(value, defaultdict):
            final_data[key] = dict(value)
        elif isinstance(value, dict):
            final_data[key] = {}
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, defaultdict):
                    final_data[key][sub_key] = dict(sub_value)
                else:
                    final_data[key][sub_key] = sub_value
        else:
            final_data[key] = value

    # 4. 결과 저장
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"{file_prefix}_tag_all.json"
    output_path = os.path.join(output_dir, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"    -> Aggregated tags saved to {output_path}")
