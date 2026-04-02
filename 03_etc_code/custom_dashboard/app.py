import os
import requests
import tweepy
from urllib.parse import urlencode, quote
from flask import Flask, render_template, request, jsonify, redirect
from dotenv import load_dotenv, set_key

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__)

# --- 각 SNS 채널별 포스팅 함수 ---

def post_to_discord(message: str, image_path: str = None) -> dict:
    """Discord 채널에 웹훅을 사용하여 메시지를 보냅니다."""
    print("[Debug] Discord 포스팅 시도 중...")
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return {"status": "error", "message": "Discord 웹훅 URL이 설정되지 않았습니다."}
    
    try:
        if image_path:
            with open(image_path, "rb") as f:
                response = requests.post(webhook_url, data={"content": message}, files={"file": f}, timeout=10)
        else:
            response = requests.post(webhook_url, json={"content": message}, timeout=10)
        response.raise_for_status()
        return {"status": "success", "message": "Discord에 성공적으로 포스팅했습니다."}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Discord 포스팅 실패: {e}"}

def post_to_twitter(message: str, image_path: str = None) -> dict:
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
        if image_path:
            # 트위터는 미디어 업로드를 위해 v1.1 API를 통해 먼저 업로드 후 트윗에 붙여야 합니다.
            auth = tweepy.OAuth1UserHandler(
                consumer_key=api_key, consumer_secret=api_secret,
                access_token=access_token, access_token_secret=access_token_secret
            )
            api = tweepy.API(auth)
            media = api.media_upload(filename=image_path)
            client.create_tweet(text=message, media_ids=[media.media_id])
        else:
            client.create_tweet(text=message)
            
        return {"status": "success", "message": "X(Twitter)에 성공적으로 트윗했습니다."}
    except Exception as e:
        error_msg = str(e)
        if "402" in error_msg:
            return {"status": "error", "message": "트위터 402 에러 : 크레딧이 부족합니다"}
        return {"status": "error", "message": f"X(Twitter) 트윗 실패: {error_msg}"}

def post_to_naver_cafe(message: str, image_path: str = None) -> dict:
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

    try: 
        if image_path:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # [중요] 이미지 첨부(multipart) 시 네이버 서버는 이중 인코딩을 해석하지 못하고 무조건 CP949(MS949)로 읽습니다.
            # 텍스트 전용 전송과 달리, 이 경우에는 반드시 텍스트를 cp949 바이트로 변환해서 보내야 한글이 깨지지 않습니다.
            # 'replace' 옵션은 이모지 등 CP949에 없는 문자가 있을 때 에러 대신 '?'로 바꿔 전송하게 해줍니다.
            data = {'subject': subject.encode('cp949', 'replace'), 'content': content.encode('cp949', 'replace')}
            
            import mimetypes
            mime_type, _ = mimetypes.guess_type(image_path)
            
            with open(image_path, 'rb') as f:
                # 명시적인 MIME 타입을 지정하여 이미지가 누락되거나 거부되는 현상 방지
                files = [('image', (os.path.basename(image_path), f, mime_type or 'image/jpeg'))]
                response = requests.post(url, headers=headers, data=data, files=files, timeout=10)
        else:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
            }
            # 네이버 카페 API의 고질적인 한글 깨짐 문제를 해결하기 위한 이중 URL 인코딩
            double_encoded_subject = quote(quote(subject))
            double_encoded_content = quote(quote(content))
            
            payload = f"subject={double_encoded_subject}&content={double_encoded_content}".encode('utf-8')
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            
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
    
    # JSON 대신 FormData로 이미지를 함께 받습니다.
    message = request.form.get("content")

    if not message:
        return jsonify({"status": "error", "message": "내용이 없습니다."}), 400

    image_file = request.files.get("image")
    image_path = None

    if image_file and image_file.filename:
        import tempfile
        from werkzeug.utils import secure_filename
        
        filename = secure_filename(image_file.filename) or "temp_image.jpg"
        image_path = os.path.join(tempfile.gettempdir(), filename)
        image_file.save(image_path)
        print(f"[Debug] 이미지 임시 저장 완료: {image_path}")

    results = {
        "discord": post_to_discord(message, image_path),
        "twitter": post_to_twitter(message, image_path),
        "naver_cafe": post_to_naver_cafe(message, image_path),
    }
    
    if image_path and os.path.exists(image_path):
        os.remove(image_path)  # 포스팅 완료 후 서버에 남은 임시 이미지 삭제

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