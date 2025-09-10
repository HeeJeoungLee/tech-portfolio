# Weekly Data Checker

네이버 클라우드 **DataBox** 를 통해 주간 단위로 공급되는 데이터를 검수하는 스크립트입니다.  
DataBox에서 제공된 데이터는 NAS 경로에 적재되고, 이후 자동화된 프로세스를 통해 Hadoop으로 복사되며 Hue에서 쿼리할 수 있게 업데이트됩니다.  
본 스크립트는 이 전체 과정에서 **Linux 경로 / Hadoop HDFS / Hue 쿼리** 3가지 관점에서 데이터를 검증합니다.  

---

## 📂 폴더 구조
```
-- weekly_data_checker  
   └─ databox_weekly_check.py   # 메인 Python 스크립트  
```

---

## ⚠️특이사항
이 코드는 네이버 클라우드 데이터박스 환경의 python 버전(2.7)에 맞게 제작되었습니다.

---

## ⚙️ 주요 기능
1. **날짜 생성 (generate_dates)**  
   - 시작일자 ~ 종료일자 범위를 받아, 하루 단위 리스트(`date=YYYY-MM-DD`)를 생성합니다.  

2. **Linux & Hadoop 검수 (execute_by_command_type)**  
   - 공급된 NAS 디렉터리(`/mnt/...`)와 Hadoop 디렉터리(`/data_v2/...`)를 비교 검수합니다.  
   - 실행되는 항목:  
     - Linux `du`, Hadoop `hadoop fs -du` → 디렉터리 용량 비교  
     - Linux `find`, Hadoop `hadoop fs -count` → 파일 개수 비교  

3. **Hue 쿼리 검수 (execute_hue_query)**  
   - Hive(Beeline) 연결을 통해 Hue 테이블에서 주간 데이터 적재 건수를 집계합니다.  
   - 예: `pro_search_click_v2`, `pro_shopping_click_v2` 의 날짜별 row count 확인  

4. **HDFS 요약 검수 (execute_hdfs_report_summary)**  
   - `hdfs dfsadmin -report` 명령을 실행해 HDFS 전체 상태(DFS Remaining, DFS Used, DFS Used%)를 요약 저장합니다.  

5. **검수 결과 저장**  
   - 실행 결과는 `/mnt/nasw1/heej/{database_name}_{YYYYMMDD}_weekly_check.txt` 파일에 기록됩니다.  

---

## ▶️ 실행 방법
```
python databox_weekly_check.py
```