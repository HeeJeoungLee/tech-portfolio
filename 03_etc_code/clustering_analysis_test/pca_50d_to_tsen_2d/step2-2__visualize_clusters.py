import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# 벡터 로드
vec_pca_50d = np.load("/root/umap_test/vectors_pca_50d.npy")
vec_tsne_2d = np.load("/root/umap_test/vectors_pca50d-to-tsne_2d.npy")

# KMeans 클러스터링 (k=8)
kmeans = KMeans(n_clusters=8, random_state=42)
labels1 = kmeans.fit_predict(vec_pca_50d)
labels2 = kmeans.fit_predict(vec_tsne_2d)

# 1. PCA 50D 결과 시각화
plt.figure(figsize=(10, 8))
plt.scatter(vec_pca_50d[:, 0], vec_pca_50d[:, 1], c=labels1, cmap="tab10", s=5)
plt.title("1024D → PCA 50D KMeans 8 clusters")
plt.xlabel("pca 1")
plt.ylabel("pca 2")
plt.tight_layout()
plt.savefig("/root/umap_test/pca-50d_result.png")
plt.show()

# 2. t-SNE 2D 결과 시각화
plt.figure(figsize=(10, 8))
plt.scatter(vec_tsne_2d[:, 0], vec_tsne_2d[:, 1], c=labels2, cmap="tab10", s=5)
plt.title("1024D → PCA 50D → t-SNE 2D KMeans 8 clusters")
plt.xlabel("t-sne 1")
plt.ylabel("t-sne 2")
plt.tight_layout()
plt.savefig("/root/umap_test/pca-to-tsne_2d_result.png")
plt.show()
