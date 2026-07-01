import requests
import base64
import json
from datetime import date
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
today = str(date.today())

for repo in repos:
    full_name = repo["full_name"]
    link = repo["html_url"]
    print(f"\n처리 중: {full_name}")

    readme_res = requests.get(f"https://api.github.com/repos/{full_name}/readme")
    if readme_res.status_code == 200:
        readme_text = base64.b64decode(readme_res.json()["content"]).decode("utf-8")
    else:
        readme_text = repo.get("description") or "설명 없음"

    # AI가 여러 값을 한 번에 JSON으로 판단
    prompt = f"""아래 GitHub README를 보고, Java/Spring 백엔드를 공부하는 초보 개발자 기준으로 판단해줘.
반드시 아래 JSON 형식으로만 답해. 다른 말/코드블록 금지.

{{
  "요약": "핵심만 5줄 이내 한국어. 배지·링크·태그 무시",
  "난이도": "쉬움 또는 보통 또는 어려움",
  "배울점": "이 프로젝트로 배울 수 있는 것 한 줄",
  "분류": "Java 또는 Spring 또는 AI 또는 Tool 중 하나",
  "블로그소재": "가능 또는 애매 또는 불가",
  "왜추천": "초보 백엔드에게 추천하는 이유 한 줄",
  "추천도": 1~10 사이 숫자
}}

프로젝트: {full_name}
README: {readme_text[:5000]}"""

    raw = client.models.generate_content(model="gemini-2.5-flash", contents=prompt).text

    # JSON만 뽑아서 파싱 (안전장치)
    try:
        raw = raw[raw.find("{"): raw.rfind("}") + 1]
        info = json.loads(raw)
    except:
        print("  ⚠️ AI 응답 파싱 실패, 건너뜀")
        continue

    score = int(info.get("추천도", 0))
    print(f"  난이도:{info.get('난이도')} 추천도:{score}")

    # 노션 저장
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "제목": {"title": [{"text": {"content": full_name}}]},
            "링크": {"url": link},
            "한국어 요약": {"rich_text": [{"text": {"content": info.get("요약", "")[:2000]}}]},
            "난이도": {"select": {"name": info.get("난이도", "보통")}},
            "배울 점": {"rich_text": [{"text": {"content": info.get("배울점", "")[:2000]}}]},
            "분류": {"multi_select": [{"name": info.get("분류", "Java")}]},
            "블로그 소재": {"select": {"name": info.get("블로그소재", "애매")}},
            "왜 추천?": {"rich_text": [{"text": {"content": info.get("왜추천", "")[:2000]}}]},
            "읽기 상태": {"select": {"name": "안 봄"}},
            "추천도": {"number": min(score, 10)},
            "저장일": {"date": {"start": today}},
        },
    }
    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
    print("  노션 응답:", res.status_code)
    if res.status_code != 200:
        print("  에러:", res.text[:300])

print("\n완료!")