import boto3
import json
import csv
from io import StringIO

def s3_csv_to_json(access_key, secret_key, bucket_name, object_name):
    if not all([access_key, secret_key, bucket_name, object_name]):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing required parameters."})
        }

    try:
        session = boto3.session.Session()
        s3_client = session.client(
            service_name='s3',
            region_name='kr-standard',
            endpoint_url='https://kr.object.ncloudstorage.com',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

        response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        csv_body = response['Body'].read().decode('utf-8')

        # 구분자 자동 감지
        sample = csv_body[:1024]
        dialect = csv.Sniffer().sniff(sample)

        reader = csv.DictReader(StringIO(csv_body), dialect=dialect)
        result_json = [row for row in reader]

        return {
            "statusCode": 200,
            "body": json.dumps(result_json, ensure_ascii=False),
            "headers": {"Content-Type": "application/json"}
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
