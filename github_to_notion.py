import requests
from config import NOTION_TOKEN, DATABASE_ID

# 1) 가져올 GitHub 저장소 (사용자명/저장소명)
REPO = "spring-projects/spring-boot"

# 2) GitHub에서 정보 가져오기
gh = requests.get(f"https://api.github.com/repos/{REPO}")
repo_data = gh.json()

title = repo_data["full_name"]          # 저장소 이름
link = repo_data["html_url"]            # 저장소 주소

print("가져온 제목:", title)
print("가져온 링크:", link)

# 3) 노션에 저장
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
}

res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
print("노션 응답:", res.status_code)