#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import datetime
import sys

script_path = "./test.sh"

# 날짜 리스트
monday_dates = [
    "2025-05-26", "2025-06-02", "2025-06-09",
    "2025-06-16", "2025-06-23", "2025-06-30"
]

# 1단계: 월요일 체크 먼저 다 돌기
all_ok = True
for date_str in monday_dates:
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        if date_obj.weekday() != 0:
            print("[✗] {} → 월요일이 아닙니다! 실행 중단.".format(date_str))
            all_ok = False
    except Exception as e:
        print("[!] {} → 날짜 형식 오류: {}".format(date_str, str(e)))
        all_ok = False

# 2단계: 모두 월요일이면 실행
if all_ok:
    print("\n✅ 모든 날짜가 월요일입니다. 스크립트 순차 실행 시작.\n")
    for date_str in monday_dates:
        print("[✓] {} → 실행 중...".format(date_str))
        p = subprocess.Popen([script_path, date_str], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout:
            sys.stdout.write(line.decode('utf-8'))
else:
    print("\n❌ 하나 이상의 날짜가 월요일이 아닙니다. 실행을 중단합니다.\n")
