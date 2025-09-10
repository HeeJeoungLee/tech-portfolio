import boto3
import json
import csv
from io import StringIO

def main(args):
    print("📍 Cloud Function 시작됨")
    print(f"입력값: {args}")

    access_key = args.get("access_key")
    secret_key = args.get("secret_key")
    bucket_name = args.get("bucket_name")
    object_name = args.get("object_name")

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
            endpoint_url='https://kr.object.private.ncloudstorage.com',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=boto3.session.Config(connect_timeout=2, read_timeout=60)
        )

        response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        csv_body = response['Body'].read().decode('utf-8')

        reader = csv.DictReader(StringIO(csv_body), delimiter='\t')
        result_json = [row for row in reader]

        print(result_json)
        return {
            "statusCode": 200,
            "body": result_json,
            "headers": {"Content-Type": "application/json"}
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }



