import requests
import base64
import json
import time
import random
from datetime import date
from google import genai
from config import NOTION_TOKEN, DATABASE_ID, GEMINI_KEY

# 카테고리별 키워드
CATEGORIES = {
    "백엔드 기본기": ["spring boot", "java backend", "rest api spring boot", "spring boot jpa"],
    "실무 감각": ["spring security jwt", "docker spring boot", "github actions java", "spring boot test"],
    "새로운 기술_AI": ["spring ai", "langchain4j", "rag spring boot", "mcp server java", "ai agent"],
    "프로젝트 아이디어": ["spring boot project", "backend project", "full stack project", "beginner backend project"],
}
# 카테고리별 뽑을 개수
PICK = {"백엔드 기본기": 2, "실무 감각": 1, "새로운 기술_AI": 2, "프로젝트 아이디어": 1}

# 오늘 검색할 키워드 랜덤 선정
keywords = []
for category, count in PICK.items():
    for kw in random.sample(CATEGORIES[category], count):
        keywords.append((category, kw))

print("오늘 검색할 키워드:")
for cat, kw in keywords:
    print(f"  [{cat}] {kw}")

client = genai.Client(api_key=GEMINI_KEY)
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
today = str(date.today())


def ask_ai(prompt, retries=3):
    for i in range(retries):
        try:
            return client.models.generate_content(
                model="gemini-2.5-flash-lite", contents=prompt
            ).text
        except Exception as e:
            print(f"  재시도 {i+1}/{retries} (에러: {str(e)[:50]})")
            time.sleep(5)
    return None


# 카테고리별로 키워드 검색 → 각 1개씩 처리
for category, kw in keywords:
    print(f"\n===== [{category}] '{kw}' 검색 =====")
    search = requests.get(
        "https://api.github.com/search/repositories",
        params={"q": kw, "sort": "stars", "per_page": 1},   # 키워드당 1개
    ).json()

    items = search.get("items", [])
    if not items:
        print("  검색 결과 없음, 건너뜀")
        continue

    repo = items[0]
    full_name = repo["full_name"]
    link = repo["html_url"]
    print(f"처리 중: {full_name}")

    readme_res = requests.get(f"https://api.github.com/repos/{full_name}/readme")
    if readme_res.status_code == 200:
        readme_text = base64.b64decode(readme_res.json()["content"]).decode("utf-8")
    else:
        readme_text = repo.get("description") or "설명 없음"

    prompt = f"""아래 GitHub README를 보고, Java/Spring 백엔드를 공부하는 초보 개발자 기준으로 판단해줘.
반드시 아래 JSON 형식으로만 답해. 다른 말/코드블록 금지.

{{
  "요약": "핵심만 5줄 이내 한국어. 배지·링크·태그 무시",
  "난이도": "쉬움 또는 보통 또는 어려움",
  "배울점": "이 프로젝트로 배울 수 있는 것 한 줄",
  "블로그소재": "가능 또는 애매 또는 불가",
  "왜추천": "초보 백엔드에게 추천하는 이유 한 줄",
  "추천도": 1~10 사이 숫자
}}

프로젝트: {full_name}
README: {readme_text[:5000]}"""

    raw = ask_ai(prompt)
    if raw is None:
        print("  ⚠️ AI 계속 실패, 건너뜀")
        continue

    try:
        raw = raw[raw.find("{"): raw.rfind("}") + 1]
        info = json.loads(raw)
    except:
        print("  ⚠️ AI 응답 파싱 실패, 건너뜀")
        continue

    score = int(info.get("추천도", 0))
    print(f"  난이도:{info.get('난이도')} 추천도:{score}")

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "제목": {"title": [{"text": {"content": full_name}}]},
            "링크": {"url": link},
            "한국어 요약": {"rich_text": [{"text": {"content": info.get("요약", "")[:2000]}}]},
            "난이도": {"select": {"name": info.get("난이도", "보통")}},
            "배울 점": {"rich_text": [{"text": {"content": info.get("배울점", "")[:2000]}}]},
            "분류": {"multi_select": [{"name": category}]},   # ← 카테고리 저장
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