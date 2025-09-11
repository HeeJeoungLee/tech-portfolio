# -*- coding: utf-8 -*-
import os
import subprocess
from datetime import datetime, timedelta

databox_name = ""
path_ver = "v3"
ncp_pro_search_path = "/mnt/pro25y2h/v3/search"
ncp_pro_shopping_path = "/mnt/pro25y2h/v3/shopping"

# 날짜 리스트 생성
def generate_dates(start_date, end_date):
    start = datetime. strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    dates = []
    for i in range((end - start).days + 1):
        date_str = (start + timedelta(days=i)).strftime('%Y-%m-%d')
        dates.append("date={}".format(date_str))
    return dates

# 명령어 실행 및 결과 기록
def write_and_run(cmd, file):
    file.write("$ {}\t\t".format(cmd))
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=open(os.devnull, 'w'), universal_newlines=True)
    except subprocess.CalledProcessError as e:
        result = e.output or "[ERROR]\n"
    file.write(result)

# Linux & Hadoop 명령어 실행
def execute_by_command_type(dates, output_file):
    path_pairs = [
        ("search", "{}/click".format(ncp_pro_search_path), "/data_{}/pro_search/click".format(path_ver)),
        ("shopping", "{}/click".format(ncp_pro_shopping_path), "/data_{}/pro_shopping/click".format(path_ver)),
    ]
    command_specs = [
        ("linux_du", "du -sh {}/{} | awk '{{print $1}}'"),
        ("hadoop_du", "hadoop fs -du -s -h {}/{} | awk '{{print $1 $2}}'"),
        ("linux_find", "find {}/{} -type f | wc -l"),
        ("hadoop_count", "hadoop fs -count {}/{} | awk '{{print $2}}'"),
    ]

    with open(output_file, "a") as f:
        for label, linux_path, hadoop_path in path_pairs:
            f.write("\n === [{}] command result === \n".format(label))
            for group_name, template in command_specs:
                path = linux_path if group_name.startswith("linux") else hadoop_path
                f.write(" --- [{}] --- \n".format(group_name))
                for date in dates:
                    cmd = template.format(path, date)
                    write_and_run(cmd, f)

# Hue 쿼리 실행
def execute_hue_query(output_file, start_date, end_date, databox_name_name):
    queries = [
        ("search_click", """
            SELECT `date`, count(*) FROM {}.pro_search_click_{} WHERE `date` BETWEEN "{}" AND "{}" GROUP BY `date`
        """.format(databox_name_name, path_ver, start_date, end_date)),
        ("shopping_click", """
            SELECT `date`, count(*) FROM {}.pro_shopping_click_{} WHERE `date` BETWEEN "{}" AND "{}" GROUP BY `date`
        """.format(databox_name_name,start_date, end_date))
    ]

    for label, query in queries:
        cmd = "beeline -u 'jdbc:hive2://m-001-hadoop:10000/{}' -e \"{}\"".format(databox_name_name, query)

        try:
            result = subprocess.check_output(cmd, shell=True, universal_newlines=True)
            lines = result.splitlines()
            data_lines = []
            inside_table = False

            for line in lines:
                if line.startswith("+") and not inside_table:
                    inside_table = True
                    data_lines.append(line)
                elif inside_table:
                    data_lines.append(line)
                    if line.strip().startswith("+") and len (data_lines) > 3:
                        break

            with open(output_file, "a") as f:
                f.write("\n === [Hue Query Result: {}] === \n".format(label))
                for line in data_lines:
                    f.write(line + "\n")

        except subprocess.CalledProcessError as e:
            with open(output_file, "a") as f:
                print("\n[ERROR] Hue query failed for [{}]\n".format(label))
                print("Return Code: {}\n".format(e.returncode))
                print("Output: {}\n".format(e.output))

def execute_hdfs_report_summary(output_file):
    try:
        result = subprocess.check_output("hdfs dfsadmin -report", shell=True, universal_newlines=True)
        lines = result.splitlines()

        summary_lines = []
        for line in lines:
            if line.startswith("DFS Remaining:") or line.startswith("DFS Used:") or line.startswith("DFS Used%:"):
                summary_lines.append(line)
            if len(summary_lines) == 3:
                break

        with open(output_file, "a") as f:
            f.write("\n=== [HDFS DFSAdmin Summary] ===\n")
            for line in summary_lines:
                f.write(line + "\n")

    except subprocess.CalledProcessError as e:
        with open(output_file, "a") as f:
            f.write("\n[ERROR] hdfs dfsadmin -report failed\n")
            f.write("Return Code: {}\n")
            f.write("Output: {}\n".format(e.output or ""))


# 메인
def main():
    #############################
    start_date = "2025-07-14"
    end_date = "2025-07-20"
    #############################
    
    dates = generate_dates(start_date, end_date)

    timestamp = datetime.now().strftime("%Y%m%d")
    output_file = "/mnt/nasw1/heej/{}_{}_weekly_check.txt".format(databox_name, timestamp)

    execute_by_command_type(dates, output_file)
    execute_hue_query(output_file, start_date, end_date)
    execute_hdfs_report_summary(output_file)
    print("[{}] weekly data check done: {}".format(databox_name, output_file))

if __name__ == "__main__":
    main()
