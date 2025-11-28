import os
import json
import numpy as np

def calculate_average_vector(input_dir, output_file):
    # 1. Vectors 폴더 내의 모든 json 파일 찾기
    files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
    
    if not files:
        print(f"'{input_dir}' 폴더에 .json 파일이 없습니다.")
        return

    print(f"총 {len(files)}개의 벡터 파일을 찾았습니다: {files}")

    vectors = []
    
    # 2. 각 파일에서 벡터 읽기
    for filename in files:
        file_path = os.path.join(input_dir, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                vector = json.load(f)
                # 리스트 형태인지 확인
                if isinstance(vector, list):
                    vectors.append(vector)
                else:
                    print(f"[WARNING] {filename}의 형식이 리스트가 아닙니다. 건너뜁니다.")
        except Exception as e:
            print(f"[ERROR] {filename} 읽기 실패: {e}")

    if not vectors:
        print("유효한 벡터가 없습니다.")
        return

    # 3. 평균 벡터 계산
    try:
        # numpy를 사용하여 열(column) 단위 평균 계산
        # axis=0은 행(row)을 따라가며 연산 -> 각 인덱스별 평균이 됨
        avg_vector = np.mean(vectors, axis=0).tolist()
        
        print(f"평균 벡터 계산 완료! (차원: {len(avg_vector)})")

        # 4. 결과 저장
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(avg_vector, f)
            
        print(f"결과가 '{output_file}'에 저장되었습니다.")

    except Exception as e:
        print(f"[ERROR] 벡터 평균 계산 중 오류 발생: {e}")
        print("모든 벡터의 차원이 동일한지 확인해주세요.")

if __name__ == "__main__":
    # 경로 설정
    INPUT_DIR = "./toVec/Vectors"
    OUTPUT_FILE = "./toVec/output.json"

    # 디렉토리 확인
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
        print(f"'{INPUT_DIR}' 폴더를 생성했습니다. 여기에 json 벡터 파일들을 넣어주세요.")
    else:
        calculate_average_vector(INPUT_DIR, OUTPUT_FILE)
