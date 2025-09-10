import json
import requests

# API Gateway 주소 + blocking/result 설정
url = (
    "http://{public_ip}:8000/s3_to_json"
)

# 요청 바디 (필요한 S3 파라미터 입력)
payload = {
    "object_name": "250618_250512-0518/test-file.csv",
    "access_key": "{access_key}",
    "secret_key": "{secret_key}",
    "bucket_name": "heej-test-bucket"
}

headers = {
    "Content-Type": "application/json"
}

# POST 요청
response = requests.post(url, json=payload, headers=headers)

# 결과 출력
print("응답 상태 코드:", response.status_code)
print("응답 JSON:")
print(json.dumps(response.json(), ensure_ascii=False, indent=2))