import os

# 토큰 수를 대략적으로 계산하는 함수 (한글의 경우 1자 ≒ 1 토큰 정도)
def count_tokens(text):
    return len(text.split())

# 텍스트 파일을 읽고 청크로 나누는 함수
def split_into_chunks(file_path, chunk_size=2000, overlap_size=100):
    # 1. 텍스트 파일 읽기
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # 2. 문단 단위로 분할 (문단은 보통 두 개의 개행으로 구분)
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    for paragraph in paragraphs:
        # 각 문단의 토큰 수 계산
        paragraph_tokens = count_tokens(paragraph)
        
        # 현재 청크에 추가해도 될 만큼 토큰 수가 적당한 경우
        if count_tokens(current_chunk) + paragraph_tokens <= chunk_size:
            current_chunk += "\n\n" + paragraph  # 문단 추가
        else:
            # 현재 청크가 너무 크면 저장하고 새로운 청크로 시작
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph  # 새 청크 시작
    
    # 마지막 남은 청크 추가
    if current_chunk:
        chunks.append(current_chunk.strip())

    # 3. 오버랩 고려한 청크 분할
    final_chunks = []
    for i in range(len(chunks)):
        if i == 0:
            final_chunks.append(chunks[i])  # 첫 번째 청크 그대로 추가
        else:
            overlap_chunk = chunks[i-1].split('\n\n')[-overlap_size:]  # 이전 청크의 마지막 몇 문단을 오버랩
            combined_chunk = "\n\n".join(overlap_chunk + chunks[i].split('\n\n')[:chunk_size])  # 오버랩 추가
            final_chunks.append(combined_chunk)
    
    return final_chunks

# 예시 실행
file_path = "./toChunk/sample.txt"
chunks = split_into_chunks(file_path, chunk_size=2000, overlap_size=2)  # 청크 크기와 오버랩 크기 조정
print(f"분할된 청크 수: {len(chunks)}")

# 청크 출력 예시 (확인용)
for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i+1} ---")
    print(chunk[:500])  # 각 청크의 앞부분 500자만 출력 (너무 길어지지 않게)

# 청크를 개별 파일로 저장하기
def save_chunks_to_files(chunks, base_filename="chunk_"):
    for i, chunk in enumerate(chunks):
        file_path = f"{base_filename}{i+1}.txt"
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(chunk)

# 예시 사용
save_chunks_to_files(chunks)
