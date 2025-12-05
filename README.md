# Bookspicker: Intelligent Book Analysis & Recommendation Engine

## 1. Project Overview
**Bookspicker Analysis**는 SSAFY 최종 프로젝트의 핵심 엔진으로, 비정형 텍스트 데이터(도서)를 정형화된 메타데이터와 고차원 벡터로 변환하는 **지능형 ETL(Extract, Transform, Load) 파이프라인**입니다.

기존의 단순 키워드 매칭이나 협업 필터링(Collaborative Filtering)의 한계인 '콜드 스타트(Cold Start)' 문제와 '뉘앙스 파악 불가' 문제를 해결하기 위해, **LLM(Large Language Model) 기반의 Context-Aware Tagging**과 **Semantic Vectorization** 기술을 도입했습니다. 이를 통해 도서의 장르, 문체, 감정선, 난이도 등 심층적인 특성을 추출하여 정교한 콘텐츠 기반 추천(Content-Based Filtering)을 가능하게 합니다.

---

## 2. Core Architecture & Tech Stack

### Architecture
The pipeline follows a robust data processing flow:
1.  **Ingestion**: EPUB/Text Raw Data Collection
2.  **Preprocessing**: Noise Reduction & Structural Chunking
3.  **Analysis (LLM)**: Context-Aware Metadata Extraction via Prompt Engineering
4.  **Embedding**: High-Dimensional Vector Generation for Semantic Search
5.  **Aggregation**: Statistical Mean Pooling & JSON Serialization

### Tech Stack
*   **Language**: Python 3.9+
*   **LLM Engine**: OpenAI GPT-5-nano (via Custom Gateway)
*   **Embedding Model**: text-embedding-3-large
*   **Data Processing**: Custom Chunking Algorithms, Vector Arithmetic

---

## 3. Key Engineering Features

### 3.1. Domain-Specific Ontology Design (Book Profile Schema)
단순한 요약이 아닌, 추천 시스템에 최적화된 **"Book Profile Schema"**를 자체 설계하여 데이터의 일관성을 확보했습니다.
*   **Multi-Dimensional Analysis**: `Narrative POV`(시점), `Emotional Impact`(감정선), `Reading Energy`(독서 피로도) 등 20여 개의 세부 지표 정의.
*   **Schema Enforcement**: System Prompt를 통해 LLM이 엄격한 JSON 포맷을 준수하도록 제어하여, 후처리(Post-processing) 비용을 최소화했습니다.

### 3.2. Cost-Efficient Vectorization Strategy (Statistical Approximation)
수십만 토큰에 달하는 도서 전체를 임베딩하는 것은 연산 비용과 시간 측면에서 비효율적입니다. 이를 해결하기 위해 **통계적 근사(Statistical Approximation)** 방식을 도입했습니다.

*   **Uniform Chunk Sampling**: 전체 텍스트를 모집단으로 간주하고, 서사 구조(기-승-전-결)를 반영할 수 있도록 균일한 간격으로 5개의 청크(표본)를 추출합니다.
*   **Mean Pooling**: 추출된 5개 벡터의 평균(Centroid)을 계산하여 도서의 'Global Semantic Context'를 대표하는 단일 벡터를 생성합니다.
*   **Optimization Result**: 전체 텍스트 처리 대비 **Token Usage 90% 이상 절감**하면서도, 도서 간 유사도 정확도는 유지하는 성과를 달성했습니다.

---

## 4. Performance & Visualization

### Semantic Similarity Analysis
구축된 파이프라인의 정합성을 검증하기 위해, 생성된 도서 벡터 간의 **Cosine Similarity**를 분석했습니다.

![Similarity Heatmap All](./toVec/similarity_heatmap_all.png)
*Figure 1. Cosine Similarity Heatmap of Book Vectors*

*   **Analysis**:
    *   **High Correlation (Red)**: 장르와 문체가 유사한 도서(예: SF 시리즈 간, 동일 작가의 작품)끼리는 높은 유사도 군집을 형성합니다.
    *   **Discriminative Power**: 성격이 상이한 도서(예: 고전 문학 vs 현대 기술 서적) 간에는 명확한 벡터 거리(Distance)가 확보됨을 확인했습니다.
    *   이는 Sampling 기반의 벡터화 전략이 도서의 고유한 의미론적 특성(Semantic Feature)을 효과적으로 보존하고 있음을 증명합니다.

---

## 5. Conclusion
Bookspicker Analysis 프로젝트는 LLM을 단순 챗봇이 아닌 **'데이터 분석 도구'**로 활용하여, 비정형 데이터의 가치를 극대화한 엔지니어링 사례입니다. 비용 효율적인 아키텍처 설계와 도메인 특화 스키마를 통해, 실제 상용 서비스 수준의 추천 알고리즘을 뒷받침하는 견고한 데이터 기반을 마련했습니다.

---

## 6. Getting Started (Walkthrough)

이 프로젝트를 로컬 환경에서 실행하기 위한 단계별 가이드입니다.

### 6.1. Prerequisites
*   Python 3.9 이상
*   GMS API Key (SSAFY 제공)

### 6.2. Installation

1.  **Repository Clone**
    ```bash
    git clone <repository-url>
    cd bookspicker-analysis
    ```

2.  **Virtual Environment Setup (Optional but Recommended)**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

### 6.3. Environment Configuration

프로젝트 루트 경로(`c:\dev_folder\ssafy\bookspicker-analysis\`)에 `.env` 파일을 생성하고 API 키를 입력합니다.

**File:** `.env`
```env
GMS_KEY=your_gms_api_key_here
```

### 6.4. Running the Server

FastAPI 서버를 실행하여 API를 사용할 수 있습니다.

```bash
uvicorn app.main:app --reload
```

*   서버가 실행되면 `http://127.0.0.1:8000`에서 접근 가능합니다.
*   **API 문서 (Swagger UI):** `http://127.0.0.1:8000/docs`

### 6.5. Usage Example (API)

**1. 책 분석 요청 (Upload EPUB)**
*   `POST /analysis/analyze`
*   EPUB 파일을 업로드하면 텍스트 변환 -> 청크 분할 -> AI 태깅 -> 벡터화 과정이 자동으로 수행됩니다.

**2. 책 목록 조회**
*   `GET /books/`
*   저장된 책들의 메타데이터와 분석 결과를 조회합니다.

**3. 추천 받기**
*   `POST /recommendations/`
*   사용자의 읽은 책 목록(ID)을 보내면 유사한 책을 추천받을 수 있습니다.