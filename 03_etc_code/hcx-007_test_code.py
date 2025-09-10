from openai import OpenAI

client = OpenAI(
    api_key="{api_key}", # CLOVA Studio API 
    base_url="https://clovastudio.stream.ntruss.com/v1/openai" # CLOVA Studio API URL
)

# Chat Completions
response = client.chat.completions.create(
    model="HCX-007",
    temperature=1,
    messages=[
        {   
            "role": "user",
            "content":"""
         안녕 너는 누구야?
        """}
    ]
)

msg = response.choices[0].message

print(" ◆ 생각 하는중:")
print(msg.reasoning_content)
print("\n◆ 최종 답변(content):")
print(msg.content)