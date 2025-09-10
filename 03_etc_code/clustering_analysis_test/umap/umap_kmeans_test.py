# UMAP 알고리즘을 이용해 1024차원 벡터를 50차원으로 축소한 뒤, 
# KMeans로 클러스터링하고 2차원으로 시각화한 분석 코드

from sklearn.cluster import KMeans 
import numpy as np 
import umap 
import matplotlib.pyplot as plt 

vectors = np.load("/root/umap_test/vectors.npy") 

# (선택) 중간 차원 축소 
reducer_50d = umap.UMAP(n_components=50, random_state=42) 
vec_50d = reducer_50d.fit_transform(vectors) 
np.save("/root/umap_test/vectors_umap_50d.npy", vec_50d)

# KMeans 
kmeans = KMeans(n_clusters=10, random_state=42) 
labels = kmeans.fit_predict(vec_50d) 

# 시각화용 2D 
vec_2d = umap.UMAP(n_components=2, random_state=42).fit_transform(vec_50d) 

# 시각화 
plt.scatter(vec_2d[:, 0], vec_2d[:, 1], c=labels, cmap="tab10", s=5) 
plt.title("KMeans on UMAP-50D, Visualized in 2D") 
plt.show() 
plt.savefig("/root/umap_test/umap_2d_result_kmeans.png")