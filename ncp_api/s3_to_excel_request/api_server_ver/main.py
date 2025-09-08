from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import json
from model.s3_to_json import s3_csv_to_json

class S3Info(BaseModel):
    access_key: Optional[str]
    secret_key: Optional[str]
    bucket_name: Optional[str]
    object_name: str

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "LG test api"}

@app.post("/s3_to_json")
def convert_s3_to_json(info: S3Info, request: Request):
    result = s3_csv_to_json(
        access_key=info.access_key,
        secret_key=info.secret_key,
        bucket_name=info.bucket_name,
        object_name=info.object_name
    )
    
    json_data = json.loads(result["body"])

    # Swagger 테스트 시, 최대 10개만 자르기
    user_agent = request.headers.get("user-agent", "")
    if ("Swagger" in user_agent or "Mozilla" in user_agent) and isinstance(json_data, list):
        json_data = json_data[:10]

    return JSONResponse(
        content={
            "result": {
                "file_name": info.object_name,
                "file_content": json_data
            }
        },
        status_code=result["statusCode"]
    )
