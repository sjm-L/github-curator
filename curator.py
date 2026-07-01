import requests
import base64
from google import genai
from config import NOTION_TOKEN, DATABASE_ID, GEMINI_KEY

KEYWORD = "spring boot"
PER_PAGE = 3

search = requests.get(
    "https://api.github.com/search/repositories",
    params={"q": KEYWORD, "sort": "stars", "per_page": PER_PAGE},
).json()
repos = search["items"]
print(f"'{KEYWORD}' 검색 결과 {len(repos)}개")

client = genai.Client(api_key=GEMINI_KEY)
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

for repo in repos:
    full_name = repo["full_name"]
    link = repo["html_url"]
    print(f"\n처리 중: {full_name}")

    readme_res = requests.get(f"https://api.github.com/repos/{full_name}/readme")
    if readme_res.status_code == 200:
        readme_text = base64.b64decode(readme_res.json()["content"]).decode("utf-8")
    else:
        readme_text = repo.get("description") or "설명 없음"

    # 핵심 요약만 (본문 번역 제거)
    summary = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"다음 README를 한국어로 핵심만 5줄 이내로 요약해줘. 배지·링크·HTML 태그는 무시하고 프로젝트 내용만. 초보자가 이해하기 쉽게:\n\n{readme_text[:5000]}",
    ).text[:2000]

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "제목": {"title": [{"text": {"content": full_name}}]},
            "링크": {"url": link},
            "한국어 요약": {"rich_text": [{"text": {"content": summary}}]},
        },
    }
    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
    print("  노션 응답:", res.status_code)

print("\n완료!")