import requests
import deepl
import base64
from config import NOTION_TOKEN, DATABASE_ID, DEEPL_KEY

REPO = "spring-projects/spring-boot"

# 1) GitHub 기본 정보
gh = requests.get(f"https://api.github.com/repos/{REPO}").json()
title = gh["full_name"]
link = gh["html_url"]

# 2) README 가져오기 (영어 원문)
readme_res = requests.get(f"https://api.github.com/repos/{REPO}/readme")
readme_text = base64.b64decode(readme_res.json()["content"]).decode("utf-8")

# 3) 너무 길면 앞부분만 (무료 한도·테스트용)
readme_text = readme_text[:3000]

# 4) DeepL 번역
translator = deepl.Translator(DEEPL_KEY)
readme_ko = translator.translate_text(readme_text, target_lang="KO").text
print("번역 완료. 글자 수:", len(readme_ko))

# 5) 노션 본문에 넣기 (2000자씩 잘라서)
def make_blocks(text):
    blocks = []
    for i in range(0, len(text), 2000):
        chunk = text[i:i+2000]
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"text": {"content": chunk}}]},
        })
    return blocks

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
    },
    "children": make_blocks(readme_ko),   # ← 본문
}
res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
print("노션 응답:", res.status_code)