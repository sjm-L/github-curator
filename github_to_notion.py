import requests
import base64
from google import genai
from config import NOTION_TOKEN, DATABASE_ID, GEMINI_KEY

REPO = "spring-projects/spring-boot"

# 1) GitHub 정보 + README 가져오기
gh = requests.get(f"https://api.github.com/repos/{REPO}").json()
title = gh["full_name"]
link = gh["html_url"]

readme_res = requests.get(f"https://api.github.com/repos/{REPO}/readme")
readme_text = base64.b64decode(readme_res.json()["content"]).decode("utf-8")

# 2) Gemini로 핵심만 한국어 요약
client = genai.Client(api_key=GEMINI_KEY)
prompt = f"다음 GitHub README를 한국어로 핵심만 5줄 이내로 요약해줘. 초보 개발자가 이해하기 쉽게:\n\n{readme_text[:5000]}"
response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
summary = response.text[:2000]   # 노션 속성 길이 안전장치
print("요약:\n", summary)

# 3) 노션에 저장 (제목 + 링크 + 한국어 요약)
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
data = {
    "parent": {"database_id": DATABASE_ID},
    "properties": {
        "제목": {"title": [{"text": {"content": title}}]},
        "링크": {"url": link},
        "한국어 요약": {"rich_text": [{"text": {"content": summary}}]},
    },
}
res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
print("노션 응답:", res.status_code)