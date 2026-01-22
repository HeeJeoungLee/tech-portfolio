import requests
import json

# 네이버 개발자 센터에서 발급받은 값
CLIENT_ID = ""
CLIENT_SECRET = ""

def search_shopping(query, display=10, start=1, sort="sim"):
    """
    네이버 쇼핑 검색 API를 호출하고,
    받은 JSON 전체를 예쁘게(들여쓰기) 출력합니다.
    """
    url = "https://openapi.naver.com/v1/search/shop.json" 

    headers = {
        "X-Naver-Client-Id": CLIENT_ID,  
        "X-Naver-Client-Secret": CLIENT_SECRET,
    }

    params = {
        "query": query,     
        "display": display,  # 한 번에 가져올 개수
        "start": start,      # 시작 위치 (1~1000)
        "sort": sort,        # sim(정확도), date(날짜), asc/dsc(가격)
    }

    response = requests.get(url, headers=headers, params=params)

    # 상태 코드 체크
    if response.status_code == 200:
        data = response.json()
        # 특정 해서 응답
        # keys = ["title", "brand", "maker"]
        # filtered_items = [{k: item.get(k) for k in keys} for item in data.get("items", [])]

        # 전체 응답(JSON)을 보기 좋게 출력
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return data
    else:
        print("요청 실패! 상태 코드:", response.status_code)
        print("응답 내용:", response.text)
        return None


if __name__ == "__main__":
    keyword = input("검색어를 입력하세요: ")
    # display 값을 100으로 하면 한 번에 최대 100개까지 가져올 수 있음
    search_shopping(keyword, display=10)
