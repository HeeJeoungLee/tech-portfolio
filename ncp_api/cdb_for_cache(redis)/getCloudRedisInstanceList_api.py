import time
import base64
import hmac
import hashlib
import requests

ACCESS_KEY = ''
SECRET_KEY = ''

timestamp = int(time.time() * 1000)
timestamp = str(timestamp)
apicall_method = "GET"
space = " "
new_line = "\n"

# API 서버 정보
api_server = "https://ncloud.apigw.ntruss.com/vredis/v2"
api_url = "/getCloudRedisInstanceList"


# hmac으로 암호화할 문자열 생성
message = apicall_method + space + api_url + new_line + timestamp + new_line + ACCESS_KEY
message = bytes(message, 'UTF-8')

# hmac_sha256 암호화
ncloud_secretkey = bytes(SECRET_KEY, 'UTF-8')
signingKey = base64.b64encode(hmac.new(ncloud_secretkey, message, digestmod=hashlib.sha256).digest())

# http 호출 헤더값 설정
http_header = {
    'x-ncp-apigw-timestamp': timestamp,
    'x-ncp-iam-access-key':  ACCESS_KEY,
    'x-ncp-apigw-signature-v2': signingKey
    }

print(signingKey)
print(ACCESS_KEY)
print(SECRET_KEY)

# api 호출
response = requests.get(api_server + api_url, headers=http_header)
print(response.text)
