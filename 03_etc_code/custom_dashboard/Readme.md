# SNS 통합 포스팅 대시보드

스트리밍 방송 공지 등 동일한 내용을 여러 SNS 채널에 한 번에 게시할 수 있는 간단한 웹 대시보드입니다.

## ✨ 주요 기능
- 웹 페이지에서 한 번의 글 작성으로 여러 SNS에 동시 포스팅
- 지원 채널:
  - Discord (웹훅 방식)
  - X (구 트위터, API v2)
  - 네이버 카페 (API)

## 🚀 시작하기

### 1. 필요 라이브러리 설치

프로젝트 폴더에서 아래 명령어를 실행하여 필요한 파이썬 라이브러리를 설치합니다.

```bash
pip install -r requirements.txt
```

### 2. API 키 및 정보 설정

` .env.example` 파일을 복사하여 `.env` 파일을 생성한 후, 각 SNS 채널에서 발급받은 자신의 API 키와 정보를 입력합니다.

```bash
# .env.example 파일을 복사하여 .env 파일 생성
cp .env.example .env 
```

이제 텍스트 에디터로 `.env` 파일을 열어 아래 값들을 채워주세요.

- **Discord**: 채널 설정에서 웹훅(Webhook)을 생성하고 URL을 복사해 `DISCORD_WEBHOOK_URL`에 붙여넣습니다.
- **X (Twitter)**: X 개발자 포털에서 앱을 생성하고 `API Key`, `API Secret`, `Access Token`, `Access Token Secret`을 발급받아 입력합니다.
- **Naver**: 네이버 개발자 센터에서 애플리케이션을 등록하고 `Client ID`, `Client Secret`을 발급받아 입력합니다.
  - `NAVER_CAFE_ID`: 글을 올릴 카페의 ID (URL에서 확인 가능)
  - `NAVER_MENU_ID`: 글을 올릴 게시판의 ID
  - `NAVER_ACCESS_TOKEN`: **(중요)** 네이버 API는 OAuth 2.0 인증이 필요하여 Access Token을 주기적으로 갱신해야 합니다. 우선 API 명세 페이지 우측의 테스트 툴에서 발급받은 임시 토큰으로 테스트해볼 수 있습니다.

### 3. 웹 서버 실행

아래 명령어로 웹 서버를 시작합니다.

```bash
python app.py
```

### 4. 대시보드 사용

웹 브라우저를 열고 `http://127.0.0.1:5000` 주소로 접속합니다.

텍스트 박스에 공지할 내용을 입력하고 '전송' 버튼을 누르면 각 채널로 포스팅이 시도되고, 결과가 화면에 표시됩니다.