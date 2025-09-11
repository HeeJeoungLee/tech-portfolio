# -*- coding: utf-8 -*-
import os
import subprocess
import random
from datetime import datetime, timedelta

databox_name = ""
path_ver = "v2"
ncp_pro_shopping_path = "/mnt/pro25zh/v3/shopping"
ncp_search_path = "/mnt/search25zh/v2/search"
ncp_shopping_path = "/mnt/shopping25zh/v3/shopping"

# Make a list of date strings like ["date=2025-06-20"]
def generate_dates(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    dates = []
    for i in range((end - start).days + 1):
        date_str = (start + timedelta(days=i)).strftime('%Y-%m-%d')
        dates.append("date={}".format(date_str))
    return random.sample(dates, min(10, len(dates)))

# Run a command and write the command + result into the output file
def write_and_run(cmd, file):
    file.write("$ {}\t\t".format(cmd))
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=open(os.devnull,'w'), universal_newlines=True)
    except subprocess.CalledProcessError as e:
        # if there is an error, write the error comment output
        result = e.output or "[ERROR]\n"
    file.write(result)

# Run Linux and Hadoop command for each date and write the results
def execute_by_command_type(ncp_pro_shopping_path, ncp_search_path, ncp_shopping_path, dates, output_file):
    # set base paths for each type (search, shopping)
    path_pairs = [
        ("shopping_purchase", "{}/purchase".format(ncp_pro_shopping_path), "/data_{}/pro_shopping/purchase".format(path_ver)),
        ("search_click", "{}/click".format(ncp_search_path), "/data_{}/search/click".format(path_ver)),
        ("search_click_cooccurrence", "{}/click_cooccurrence".format(ncp_search_path), "/data_{}/search/click_cooccurrence".format(path_ver)),
        ("search_click_location", "{}/click_location".format(ncp_search_path), "/data_{}/search/click_location".format(path_ver)),
        ("shopping_click", "{}/click".format(ncp_shopping_path), "/data_{}/shopping/click".format(path_ver)),
        ("shopping_click_cooccurrence", "{}/click_cooccurrence".format(ncp_shopping_path), "/data_{}/shopping/click_cooccurrence".format(path_ver)),
        ("shopping_purchase", "{}/purchase".format(ncp_shopping_path), "/data_{}/shopping/purchase".format(path_ver)),
        ("shopping_purchase_cooccurrence", "{}/purchase_cooccurrence".format(ncp_shopping_path), "/data_{}/shopping/purchase_cooccurrence".format(path_ver)),
    ]

    # list of commands to run
    command_specs = [
        ("linux_du", "du -sh {}/{} | awk '{print $1}'"),
        ("hadoop_du", "hadoop fs -du -s -h {}/{} | awk '{{print $1 $2}}'"),
        ("linux_find", "find {}/{} -type f | wc -l"),
        ("hadoop_count", "hadoop fs -count {}/{} | awk '{{print $2}}'")
    ]

    with open(output_file, "a") as f:
        for label, linux_path, hadoop_path in path_pairs:
            f.write("=== [{}] COMMAND RESULT ===\n".format(label))
            for group_name, template in command_specs:
                # Choose correct path (Linux or hadoop)
                path = linux_path if group_name.startswith("linux") else hadoop_path
                cmd = template.format(path)
                f.write("--- [{}] ---\n".format(group_name))
                for date in dates:
                    cmd_date = "{} {}".format(cmd, date)
                    write_and_run(cmd_date, f)
            f.write("\n")

# Run Hive querys and save table summary
def execute_hue_query(databox_name, path_ver, output_file, start_date, end_date):
    hue_queries = [
        ("pro_shopping_purchase", """
            SELECT `date`, count(*) FROM {}.pro_shopping_purchase_{} WHERE `date` BETWEEN '{}' AND '{}' GROUP BY `date` ORDER BY `date`
        """.format(databox_name, path_ver, start_date, end_date)),
        ("search_click", """
            SELECT `date`, count(*) FROM {}.search_click_{} WHERE `date` BETWEEN '{}' AND '{}' GROUP BY `date` ORDER BY `date`
        """.format(databox_name, path_ver, start_date, end_date)),
        ("search_click_cooccurrence", """
            SELECT `date`, count(*) FROM {}.search_click_cooccurrence_{} WHERE `date` BETWEEN '{}' AND '{}' GROUP BY `date` ORDER BY `date`
        """.format(databox_name, path_ver, start_date, end_date)),
        ("search_location", """
            SELECT `date`, count(*) FROM {}.search_location_{} WHERE `date` BETWEEN '{}' AND '{}' GROUP BY `date` ORDER BY `date`
        """.format(databox_name, path_ver, start_date, end_date)),
        ("shopping_click", """
            SELECT `date`, count(*) FROM {}.shopping_click_{} WHERE `date` BETWEEN '{}' AND '{}' GROUP BY `date` ORDER BY `date`
        """.format(databox_name, path_ver, start_date, end_date)),
        ("shopping_click_cooccurrence", """
            SELECT `date`, count(*) FROM {}.shopping_click_cooccurrence_{} WHERE `date` BETWEEN '{}' AND '{}' GROUP BY `date` ORDER BY `date`
        """.format(databox_name, path_ver, start_date, end_date)),
        ("shopping_purchase", """
            SELECT `date`, count(*) FROM {}.shopping_purchase_{} WHERE `date` BETWEEN '{}' AND '{}' GROUP BY `date` ORDER BY `date`
        """.format(databox_name, path_ver, start_date, end_date)),
        ("shopping_purchase_cooccurrence", """
            SELECT `date`, count(*) FROM {}.shopping_purchase_cooccurrence_{} WHERE `date` BETWEEN '{}' AND '{}' GROUP BY `date` ORDER BY `date`
        """.format(databox_name, path_ver, start_date, end_date)),
    ]

    for label, query in hue_queries:
        # Hive query command using beeline
        cmd = "beeline -u 'jdbc:hive2://m-081-hadoop-hd:10000/{}' -e \"{}\"".format(databox_name, query)

        try:
            # Run the query
            result = subprocess.check_output(cmd, shell=True, universal_newlines=True)
            lines = result.splitlines()
            table_lines = []
            in_table = False

            # Extract the table part (skip borders like +---+)
            for line in lines:
                if line.strip().startswith("+") and not in_table:
                    in_table = True
                    table_lines.append(line)
                elif in_table:
                    table_lines.append(line)
                    if line.strip().startswith("+") and len(table_lines) > 3:
                        break

            with open(output_file, "a") as f:
                f.write("\n=== {} Hue COMMAND RESULT ===\n".format(label))
                for line in table_lines:
                    f.write(line + "\n")

        except subprocess.CalledProcessError as e:
            with open(output_file, "a") as f:
                print("\n[ERROR] hive query failed\n")
                print("Return code: {}".format(e.returncode))
                print("Output: {}".format(e.output))

# Get the DFS summary from HDFS admin report (total status only)
def execute_hdfs_report_summary(output_file):
    try:
        result = subprocess.check_output("hdfs dfsadmin -report", shell=True, universal_newlines=True)
        lines = result.splitlines()

        summary_lines = []
        for line in lines:
            if line.startswith("DFS Remaining") or line.startswith("DFS Used") or line.startswith("DFS Used%") :
                summary_lines.append(line)
            if len(summary_lines) == 3:
                break

        with open(output_file, "a") as f:
            f.write("\n=== [HDFS DFSAdmin report Summary] === \n")
            for line in summary_lines:
                f.write(line + "\n")

    except subprocess.CalledProcessError as e:
        with open(output_file, "a") as f:
            f.write("\n[ERROR] hdfs dfsadmin -report failed\n")
            f.write("Return Code: {}\n".format(e.returncode))
            f.write("Output: {}\n".format(e.output or ""))

def main():
    #### set date range ######
    start_date = "2025-07-26"
    end_date = "2025-07-31"
    ##########################
    dates = generate_dates(start_date, end_date)

    timestamp = datetime.now().strftime("%Y%m%d")
    output_file = "/mnt/nasw1/hedj/check_log/{}_{}_monthly_check.txt".format(databox_name, timestamp)

    execute_by_command_type(ncp_pro_shopping_path, ncp_search_path, ncp_shopping_path, dates, output_file)
    execute_hue_query(databox_name, path_ver, output_file, start_date, end_date)
    execute_hdfs_report_summary(output_file)

    print("[{}] monthly data check done: {}".format(databox_name, output_file))

if __name__ == "__main__":
    main()
