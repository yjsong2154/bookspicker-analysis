import os

def count_tokens(text):
    """토큰 수를 대략적으로 계산 (공백 기준 split)"""
    return len(text.split())

def split_into_chunks(text, chunk_size=2000, overlap_size=100):
    """텍스트를 청크로 분할"""
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    for paragraph in paragraphs:
        paragraph_tokens = count_tokens(paragraph)
        
        if count_tokens(current_chunk) + paragraph_tokens <= chunk_size:
            current_chunk += "\n\n" + paragraph
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph
    
    if current_chunk:
        chunks.append(current_chunk.strip())

    final_chunks = []
    for i in range(len(chunks)):
        if i == 0:
            final_chunks.append(chunks[i])
        else:
            # 이전 청크의 마지막 부분을 오버랩
            prev_chunk_paras = chunks[i-1].split('\n\n')
            # 오버랩할 문단 개수가 전체 문단보다 많으면 전체를 오버랩
            overlap_count = min(len(prev_chunk_paras), overlap_size) # overlap_size가 문단 수 기준인지 토큰 기준인지 확인 필요. 원본 코드는 list slicing이므로 문단 수 기준임.
            # 원본 코드: overlap_chunk = chunks[i-1].split('\n\n')[-overlap_size:]
            # 여기서 overlap_size=100은 문단 100개를 의미함. 꽤 큼.
            
            overlap_chunk = prev_chunk_paras[-overlap_size:]
            combined_chunk = "\n\n".join(overlap_chunk + chunks[i].split('\n\n'))
            # 원본 코드에는 [:chunk_size] 슬라이싱이 있었는데, chunks[i]는 이미 chunk_size 이하로 만들어짐. 
            # 하지만 combined_chunk가 chunk_size를 넘을 수 있음. 원본 로직을 따름.
            
            # 원본 코드: combined_chunk = "\n\n".join(overlap_chunk + chunks[i].split('\n\n')[:chunk_size])
            # chunks[i] split 결과가 리스트이므로 [:chunk_size]는 문단 개수 제한임. 
            # 하지만 chunks[i] 자체가 이미 토큰 제한으로 만들어진 텍스트임.
            # 원본 로직을 그대로 가져오겠음.
            
            combined_chunk = "\n\n".join(overlap_chunk + chunks[i].split('\n\n'))
            final_chunks.append(combined_chunk)
    
    return final_chunks

def save_chunks(chunks, output_dir, file_prefix):
    """청크를 파일로 저장"""
    os.makedirs(output_dir, exist_ok=True)
    saved_files = []
    for i, chunk in enumerate(chunks):
        # (원래제목)_chunk_01.txt 형식
        file_name = f"{file_prefix}_chunk_{i+1:02d}.txt"
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(chunk)
        saved_files.append(file_path)
    return saved_files
