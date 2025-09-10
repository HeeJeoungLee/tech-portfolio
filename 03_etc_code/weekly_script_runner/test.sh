#!/bin/bash

DATE=$1
YEAR=${DATE:0:4}
MONTH=${DATE:5:2}
DAY=${DATE:8:2}

echo "입력한 날짜: $DATE"
echo "연도: $YEAR"
echo "월: $MONTH"
echo "일: $DAY"
