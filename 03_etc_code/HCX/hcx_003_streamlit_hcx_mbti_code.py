import json
import http.client
import urllib.parse  # URL 파싱을 위해 추가
import streamlit as st

def execute_completion_request(preset_text):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'X-NCP-CLOVASTUDIO-API-KEY': "{clova_studio_api_key}",
        'X-NCP-APIGW-API-KEY': "{apigw_api_key}",
        'X-NCP-CLOVASTUDIO-REQUEST-ID': "{clova_studio_request_id}"
    }
   
    full_url = "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003"
    parsed_url = urllib.parse.urlparse(full_url)  # URL 파싱
    host = parsed_url.netloc  # 호스트 추출
    path = parsed_url.path  # 경로 추출
 
    request_data = {
        'messages': preset_text,
        'maxTokens': 100,
        'temperature': 0.5,
        'topK': 0,
        'topP': 0.8,
        'repeatPenalty': 5.0,
        'stopBefore': [],
        'includeTokens': True,
        'includeAiFilters': True,
        'includeProbs': True
    }
   
    conn = http.client.HTTPSConnection(host)
    conn.request('POST', path, json.dumps(request_data), headers)  # 경로 그대로 사용
    response = conn.getresponse()
    result = json.loads(response.read().decode('utf-8'))
    conn.close()
   
    if result['status']['code'] == '20000':
        return result
    else:
        return f"Error: {result}"
   


st.title('MBTI 대백과사전')
question = st.text_input(
    '질문', 
    placeholder='질문을 입력해 주세요'
)

if question:
    preset_text = [
    {"role": "system", "content": "안녕하세요 MBTI 박사입니다 무엇을 도와드릴까요?"},
    {"role": "user", "content": question},
]

    response_text = execute_completion_request(preset_text)
    assistant_response = response_text["result"]["message"]["content"]
    st.markdown(f"**응답:** {assistant_response}")
