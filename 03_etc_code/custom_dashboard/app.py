import os
import requests
import tweepy
from urllib.parse import urlencode
from flask import Flask, render_template, request, jsonify, redirect
from dotenv import load_dotenv, set_key

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__)

# --- 각 SNS 채널별 포스팅 함수 ---

def post_to_discord(message: str) -> dict:
    """Discord 채널에 웹훅을 사용하여 메시지를 보냅니다."""
    print("[Debug] Discord 포스팅 시도 중...")
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return {"status": "error", "message": "Discord 웹훅 URL이 설정되지 않았습니다."}
    
    try:
        response = requests.post(webhook_url, json={"content": message}, timeout=10)
        response.raise_for_status()
        return {"status": "success", "message": "Discord에 성공적으로 포스팅했습니다."}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Discord 포스팅 실패: {e}"}

def post_to_twitter(message: str) -> dict:
    """X (Twitter)에 API v2를 사용하여 트윗을 게시합니다."""
    print("[Debug] X (Twitter) 포스팅 시도 중...")
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    print(f"[Debug] Twitter API Key 확인: {str(api_key)[:5]}...")
    print(f"[Debug] Twitter Access Token 확인: {str(access_token)[:5]}...")

    if not all([api_key, api_secret, access_token, access_token_secret]):
        return {"status": "error", "message": "X(Twitter) API 키가 모두 설정되지 않았습니다."}

    try:
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        client.create_tweet(text=message)
        return {"status": "success", "message": "X(Twitter)에 성공적으로 트윗했습니다."}
    except Exception as e:
        return {"status": "error", "message": f"X(Twitter) 트윗 실패: {e}"}

def post_to_naver_cafe(message: str) -> dict:
    """네이버 카페에 API를 사용하여 게시글을 작성합니다."""
    print("[Debug] Naver Cafe 포스팅 시도 중...")
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    access_token = os.getenv("NAVER_ACCESS_TOKEN")
    cafe_id = os.getenv("NAVER_CAFE_ID")
    menu_id = os.getenv("NAVER_MENU_ID")

    if not all([client_id, client_secret, access_token, cafe_id, menu_id]):
        return {"status": "error", "message": "네이버 카페 API 정보가 모두 설정되지 않았습니다."}

    # 네이버 카페 API는 제목과 본문을 별도로 받습니다.
    # 간단히 메시지의 첫 줄을 제목으로, 나머지를 본문으로 사용합니다.
    lines = message.split('\n')
    subject = lines[0]
    content = '\n'.join(lines[1:]) if len(lines) > 1 else subject

    url = f"https://openapi.naver.com/v1/cafe/{cafe_id}/menu/{menu_id}/articles"
    
    print(f"[Debug] Naver URL 확인: {url}")
    print(f"[Debug] Naver Token 미리보기: {access_token[:15]}...")
    print(f"[Debug] Naver 제목 확인: {subject}")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    # API는 'subject'와 'content'를 필수로 요구합니다.
    data = {
        'subject': subject,
        'content': content
    }

    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        return {"status": "success", "message": "네이버 카페에 성공적으로 포스팅했습니다."}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"네이버 카페 포스팅 실패: {e.response.text}"}


# --- Flask 라우트 ---

@app.route("/")
def index():
    """메인 페이지를 렌더링합니다."""
    return render_template("index.html")

@app.route("/post", methods=["POST"])
def handle_post():
    """클라이언트로부터 메시지를 받아 각 채널에 포스팅합니다."""
    print("\n[Debug] 클라이언트로부터 /post 요청을 받았습니다.")
    data = request.get_json()
    message = data.get("content")

    if not message:
        return jsonify({"status": "error", "message": "내용이 없습니다."}), 400

    results = {
        "discord": post_to_discord(message),
        "twitter": post_to_twitter(message),
        "naver_cafe": post_to_naver_cafe(message),
    }
    print("[Debug] 모든 포스팅 완료. 결과를 클라이언트로 반환합니다.")
    return jsonify(results)

# --- 네이버 API 토큰 발급 라우트 ---

@app.route("/naver_auth")
def naver_auth():
    """네이버 로그인 페이지로 리다이렉트하여 인증 코드를 요청합니다."""
    client_id = os.getenv("NAVER_CLIENT_ID")
    redirect_uri = "http://127.0.0.1:5000/naver_callback"
    
    url = "https://nid.naver.com/oauth2.0/authorize?" + urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": "CUSTOM_DASHBOARD_STATE"
    })
    return redirect(url)

@app.route("/naver_callback")
def naver_callback():
    """네이버 로그인 후 반환된 코드로 Access Token을 발급받아 .env에 저장합니다."""
    code = request.args.get("code")
    state = request.args.get("state")
    
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    
    url = f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&code={code}&state={state}"
    
    response = requests.get(url)
    data = response.json()
    
    if "access_token" in data:
        access_token = data["access_token"]
        # .env 파일 업데이트 및 현재 프로세스의 환경 변수 적용
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        set_key(env_path, "NAVER_ACCESS_TOKEN", access_token)
        os.environ["NAVER_ACCESS_TOKEN"] = access_token
        
        return f"<h3>네이버 토큰 자동 발급 성공! (.env 파일에 저장되었습니다)</h3><p>토큰: {access_token[:15]}...</p><br><a href='/'>대시보드로 돌아가기</a>"
    else:
        return f"<h3>토큰 발급 실패</h3><p>{data}</p><br><a href='/'>대시보드로 돌아가기</a>"

if __name__ == "__main__":
    # host='0.0.0.0'으로 설정하면 외부에서도 접속 가능합니다.
    app.run(host="127.0.0.1", port=5000, debug=True)