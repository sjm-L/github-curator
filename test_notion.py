import requests
from config import NOTION_TOKEN, DATABASE_ID

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

data = {
    "parent": {"database_id": DATABASE_ID},
    "properties": {
        "제목": {"title": [{"text": {"content": "테스트 글"}}]}
    },
}

res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
print(res.status_code)
print(res.text)