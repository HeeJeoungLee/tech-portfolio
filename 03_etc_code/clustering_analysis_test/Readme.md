# Clustering Analysis Test

이 폴더는 **OpenSearch에서 추출한 벡터 데이터에 대해 차원 축소 및 KMeans 클러스터링을 수행**하는 코드 모음입니다.  
전체 워크플로우는 크게 **벡터 수집 → 차원 축소 → 최적 클러스터 수 분석**으로 구성됩니다.

---

## 📂 파일 구성

### 1. `step1__fetch_vectors.py`
- **목적**: OpenSearch 인덱스(`hms_claim_archive`)에서 모든 `vector_field` 값을 비동기로 수집하여 `vectors.npy` 파일로 저장
- **주요 기능**
  - AsyncOpenSearch + Scroll API를 사용해 벡터 전량 추출
  - 결과를 NumPy 배열로 변환 후 `.npy` 포맷으로 저장
- **출력**
  - `vectors.npy` (shape: `(N, 1024)`)

---

### 2. `step2-1__reduce_dimension.py`
- **목적**: 고차원 벡터를 차원 축소하여 분석 및 시각화에 활용
- **단계**
  1. PCA: 1024차원 → 50차원 축소
  2. t-SNE: 50차원 → 2차원 축소
- **출력**
  - `vectors_pca_50d.npy`  
  - `vectors_pca50d-to-tsne_2d.npy`

---

### 3. `step2-2__visualize_clusters.py`
- **목적**: 축소된 벡터를 KMeans로 군집화하고 시각화
- **내용**
  - PCA 50D 및 t-SNE 2D 결과에 대해 각각 `KMeans (k=8)` 수행
  - Matplotlib으로 2D 산점도 시각화
- **출력 이미지**
  - `pca-50d_result.png`  
  - `pca-to-tsne_2d_result.png`

---

### 4. `step3__cluster_analysis.py`
- **목적**: KMeans 클러스터 개수 최적화
- **분석 방법**
  - Elbow Method (Inertia)
  - Silhouette Score
  - Davies-Bouldin Index
  - GAP Statistic
- **출력**
  - `elbow.png`  
  - `silhouette.png`

---

## ⚙️ 실행 순서
   1. **벡터 수집**
   ```
   python step1__fetch_vectors.py
   ```
   2-1. **차원 축소**
   ```
   python step2-1__reduce_dimension.py
   ```
   2-2. **차원 축소 알고리즘 별 시각화**
   ```
   python step2-2__visualize_clusters.py
   ```
   3. 클러스터 개수 분석
   ```
   python step3__cluster_analysis.py
   ```
