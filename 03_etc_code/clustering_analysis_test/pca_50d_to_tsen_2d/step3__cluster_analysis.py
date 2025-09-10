# KMeans 기반 군집 수 최적화 분석
import time 
import numpy as np 
from sklearn.manifold import TSNE 
from sklearn.cluster import KMeans 
from sklearn.metrics import silhouette_score, davies_bouldin_score 
from sklearn.decomposition import PCA 
import matplotlib.pyplot as plt 
from sklearn.metrics import pairwise_distances 
from sklearn.utils import resample 
from tqdm import tqdm 

vec_2d = np.load("/root/umap_test/vectors_pca50d-to-tsne_2d.npy") 

# ✅ 3. 클러스터 수 탐색 (엘보우 & 실루엣) 
inertias = [] 
silhouettes = [] 
gap_stats = [] 
davies_bouldins = [] 

K_range = range(2, 50) 
print("\n▶ 클러스터 수 분석 (Elbow & Silhouette)...") 

for k in K_range: 
    kmeans = KMeans(n_clusters=k, random_state=42) 
    labels = kmeans.fit_predict(vec_2d) 
    
    # Inertia (Elbow) 
    inertias.append(kmeans.inertia_) 
    
    # Silhouette 
    sil_score = silhouette_score(vec_2d, labels) 
    silhouettes.append(sil_score) 
    
    # Davies-Bouldin Index 
    db_score = davies_bouldin_score(vec_2d, labels) 
    davies_bouldins.append(db_score) 

# GAP 통계량 계산 함수 
def compute_gap_statistic(data, n_refs=5, max_k=50): 
    gaps = [] 
    for k in tqdm(range(2, max_k), desc="▶ GAP Statistic 계산 중"): 
        km = KMeans(n_clusters=k, random_state=42) 
        km.fit(data) 
        intra_dists = km.inertia_ 
        
        ref_dists = []
        for _ in range(n_refs): 
            reference = np.random.uniform(
                low=np.min(data, axis=0), 
                high=np.max(data, axis=0), 
                size=data.shape 
            ) 
            km_ref = KMeans(n_clusters=k, random_state=42).fit(reference) 
            ref_dists.append(km_ref.inertia_) 
    
        log_ref = np.log(np.mean(ref_dists)) 
        gap = log_ref - np.log(intra_dists) 
        gaps.append(gap) 
    return gaps 
    
# Gap Statistic (별도로 계산) 
gap_stats = compute_gap_statistic(vec_2d, n_refs=5, max_k=max(K_range)+1) 

#---------------------------------------------
plt.figure(figsize=(10, 8)) # 캔버스 사이즈 
#Elbow 
plt.subplot(2, 2, 1) # 캔버스 2행, 2열로 쪼갰을 때 1번째 
plt.plot(K_range, inertias, marker='o') 
plt.title("Elbow Method (Inertia)") # 표 제목 
plt.xlabel("Number of Clusters (k)") # x축 
plt.ylabel("Inertia") # y축 
#plt.grid(True) 
plt.tight_layout() 
plt.savefig("/root/umap_test/elbow.png") 

# Silhouette 
plt.subplot(2, 2, 2) 
plt.plot(K_range, silhouettes, marker='o', color='green') 
plt.title("Silhouette Score") 
plt.xlabel("Number of Clusters (k)") 
plt.ylabel("Score") 
# plt.grid(True) 
plt.tight_layout() 
plt.savefig("/root/umap_test/silhouette.png")