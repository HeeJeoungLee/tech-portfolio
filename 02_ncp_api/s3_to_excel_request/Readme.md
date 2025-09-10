# 프로젝트 개요

이 레포지토리는 **네이버 클라우드(NCP) 기반 API 서버 구현**을 두 가지 방식으로 제공합니다.

1. **api_server_ver**  
   - FastAPI 기반의 서버 실행 버전  
   - 동작 방식:
     - 서버를 직접 실행하여 API 요청을 처리
     - 네이버 클라우드 **Object Storage(S3)** 에 저장된 CSV 파일을 읽어와 JSON 형태로 응답
   - 특징:
     - 서버가 상시 실행되어야 함
     - 커스터마이징이 자유롭고, 로컬/VM 환경에서 실행 가능

2. **ncp_api_gw_ver**  
   - **서버리스(Serverless) 아키텍처** 버전  
   - 동작 방식:
     - 네이버 클라우드 **Cloud Function**에 코드를 배포
     - **API Gateway**를 트리거로 설정 → Gateway 요청이 오면 Function이 실행되어 응답
   - 특징:
     - 서버 운영 불필요 (Serverless)
     - 요청이 있을 때만 실행되어 비용 효율적
     - 확장성과 관리 용이성이 높음
     - Cloud Function 제약 사항이 있음

---

## 폴더 구조
```.
├── api_server_ver/     # FastAPI 실행형 버전
└── ncp_api_gw_ver/     # Cloud Function + API Gateway 서버리스 버전
```
