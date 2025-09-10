# 1. OpenSearch에서 모든 vector_field 벡터를 비동기로 가져와서 vectors.npy로 저장
import asyncio
import numpy as np
# import umap
from opensearchpy import AsyncOpenSearch
from tqdm.asyncio import tqdm_asyncio

INDEX_NAME = "hms_claim_archive"
VECTOR_FIELD = "vector_field"

# OpenSearch 연결 변수 설정
opensearch_client = AsyncOpenSearch(
    hosts=["https://10.122.2.198:9200", "https://10.122.2.199:9200"],
    http_auth=('cloocus', 'cloocus123!'),
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)

# ✅ 문서에서 vector_field만 추출하는 함수
async def fetch_vectors(index_name: str, field: str):
    vectors = []

    # Scroll API 사용
    query = {
        "_source": [field],
        "query": {"match_all": {}}
    }

    scroll = "2m"
    batch_size = 1000

    response = await opensearch_client.search(
        index=index_name,
        body=query,
        scroll=scroll,
        size=batch_size
    )

    scroll_id = response["_scroll_id"]
    hits = response["hits"]["hits"]

    while hits:
        for doc in hits:
            vector = doc["_source"].get(field)
            if vector:
                vectors.append(vector)

        response = await opensearch_client.scroll(
            scroll_id=scroll_id,
            scroll=scroll
        )
        scroll_id = response["_scroll_id"]
        hits = response["hits"]["hits"]
    return np.array(vectors, dtype=np.float32)


async def main():
    vectors = await fetch_vectors(INDEX_NAME, VECTOR_FIELD)
    np.save("/home/cloocus/dev/heej/vector_umap_test/vectors.npy", vectors)
    print("✅ vectors.npy 저장 완료")

# # ✅ 메인 실행 함수
# async def main():
#     print("📥 벡터 불러오는 중...")
#     vectors = await fetch_vectors(INDEX_NAME, VECTOR_FIELD)
#     print(f"✅ 불러온 벡터 수: {len(vectors)}, 차원: {len(vectors[0])}")

#     # UMAP 2D
#     print("📊 UMAP 2D 축소 중...")
#     reducer_2d = umap.UMAP(n_components=2, random_state=42)
#     vectors_2d = reducer_2d.fit_transform(vectors)
#     print("✅ UMAP 2D 완료")

#     # UMAP 50D
#     print("📊 UMAP 50D 축소 중...")
#     reducer_50d = umap.UMAP(n_components=50, random_state=42)
#     vectors_50d = reducer_50d.fit_transform(vectors)
#     print("✅ UMAP 50D 완료")

#     return vectors_2d, vectors_50d


# ✅ 실행
if __name__ == "__main__":
    # vectors_2d, vectors_50d = asyncio.run(main())
    asyncio.run(main())