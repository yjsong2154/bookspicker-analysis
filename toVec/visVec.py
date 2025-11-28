import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.font_manager as fm

def visualize_similarity(input_dir, output_image):
    # 1. Vectors_cal 폴더 내의 모든 json 파일 찾기
    files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
    
    if not files:
        print(f"'{input_dir}' 폴더에 .json 파일이 없습니다.")
        return

    print(f"총 {len(files)}개의 벡터 파일을 찾았습니다: {files}")

    vectors = []
    labels = []

    # 2. 각 파일에서 벡터 읽기
    for filename in files:
        file_path = os.path.join(input_dir, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                vector = json.load(f)
                if isinstance(vector, list):
                    vectors.append(vector)
                    # 파일명에서 확장자 제거하여 라벨로 사용
                    labels.append(os.path.splitext(filename)[0])
                else:
                    print(f"[WARNING] {filename}의 형식이 리스트가 아닙니다.")
        except Exception as e:
            print(f"[ERROR] {filename} 읽기 실패: {e}")

    if len(vectors) < 2:
        print("비교할 벡터가 충분하지 않습니다 (최소 2개 필요).")
        return

    # 3. 코사인 유사도 계산
    try:
        # sklearn의 cosine_similarity 사용 (입력은 2D 배열이어야 함)
        sim_matrix = cosine_similarity(vectors)
        
        print("유사도 행렬 계산 완료.")

        # 4. 시각화 (Heatmap)
        plt.figure(figsize=(10, 8))
        
        # 한글 폰트 설정 (Windows 기본 맑은 고딕 시도)
        # 시스템에 따라 폰트가 다를 수 있으므로 예외처리
        try:
            plt.rcParams['font.family'] = 'Malgun Gothic'
        except:
            print("[WARNING] 한글 폰트 설정 실패, 기본 폰트를 사용합니다.")

        # 마이너스 기호 깨짐 방지
        plt.rcParams['axes.unicode_minus'] = False

        # Heatmap 그리기
        # cmap='RdBu_r' : Red(높음) <-> Blue(낮음), _r은 reverse (Red가 1에 가깝게)
        # center=0 : 0을 흰색으로
        # vmin=-1, vmax=1 : 코사인 유사도 범위
        sns.heatmap(sim_matrix, annot=True, fmt=".2f", cmap='RdBu_r', 
                    xticklabels=labels, yticklabels=labels,
                    vmin=-1, vmax=1, center=0)

        plt.title("Vector Cosine Similarity")
        plt.tight_layout()

        # 저장 및 출력
        plt.savefig(output_image)
        print(f"히트맵 이미지가 '{output_image}'에 저장되었습니다.")
        # plt.show() # 서버 환경 등에서는 주석 처리

    except Exception as e:
        print(f"[ERROR] 시각화 중 오류 발생: {e}")

if __name__ == "__main__":
    # 경로 설정
    INPUT_DIR = "./toVec/Vectors_cal"
    OUTPUT_IMAGE = "./toVec/similarity_heatmap.png"

    # 디렉토리 확인
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
        print(f"'{INPUT_DIR}' 폴더를 생성했습니다. 여기에 비교할 json 벡터 파일들을 넣어주세요.")
    else:
        visualize_similarity(INPUT_DIR, OUTPUT_IMAGE)
