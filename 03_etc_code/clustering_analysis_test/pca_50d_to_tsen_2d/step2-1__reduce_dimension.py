# 2. 벡터 차원 축소 (PCA → t-SNE)
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import time

# 1. 원본 벡터 로드
vectors = np.load("/root/umap_test/vectors.npy")  # (160000, 1024)

# 2. PCA로 50차원 축소
print("▶ PCA 50D 차원 축소 중...")
start = time.time()
pca = PCA(n_components=50, random_state=42)
vec_50d = pca.fit_transform(vectors)
np.save("/root/umap_test/vectors_pca_50d.npy", vec_50d)
print(f"✅ PCA 완료! 소요 시간: {round(time.time() - start, 2)}초")

# 3. t-SNE로 2차원 축소
print("▶ t-SNE 2D 차원 축소 중...")
start = time.time()
tsne = TSNE(n_components=2, random_state=42, perplexity=30, max_iter=1000)
vec_2d = tsne.fit_transform(vec_50d)
np.save("/root/umap_test/vectors_pca50d-to-tsne_2d.npy", vec_2d)
print(f"✅ t-SNE 완료! 소요 시간: {round(time.time() - start, 2)}초")

# (선택) 시각화
plt.figure(figsize=(10, 8))
plt.scatter(vec_2d[:, 0], vec_2d[:, 1], s=5, alpha=0.6)
plt.title("t-SNE 2D Projection (after PCA 50D)")
plt.savefig("/root/umap_test/tsne_2d_projection.png")
plt.show()
