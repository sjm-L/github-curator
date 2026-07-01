# github-curator

Java/Spring 백엔드를 공부하는 초보 개발자를 위한 **GitHub 자료 자동 큐레이터**입니다.
영어로 된 GitHub 저장소를 매일 자동으로 찾아, **한국어로 요약**하고 **Notion에 정리**해 줍니다.

---

## 왜 만들었나

- GitHub 게시글이 영어라 잘 안 읽게 되고, 좋은 자료를 놓치는 문제가 있었습니다.
- 너무 많은 기술 중 "내게 필요하고 흥미로운 것"만 골라 보고 싶었습니다.
- 그래서 **수집 → 번역·요약 → 정리**를 사람이 매번 하지 않고 자동으로 처리하도록 만들었습니다.

---

## 주요 기능

| 단계 | 기능                                                  |
| ---- | ----------------------------------------------------- |
| 1    | GitHub 저장소 정보(제목·링크)를 Notion DB에 저장      |
| 2    | README를 한국어로 핵심 요약                           |
| 3    | 카테고리별 키워드로 여러 저장소 자동 수집             |
| 4    | AI가 난이도·추천도·배울 점 등 속성을 자동 판단해 채움 |
| 5    | 매일 아침 7시 자동 실행 (macOS launchd)               |

---

## 동작 흐름

```
카테고리별 키워드 랜덤 선정
        ↓
GitHub 검색 API로 저장소 수집
        ↓
README 가져오기 (base64 디코딩)
        ↓
Gemini AI로 한국어 요약 + 속성 판단(JSON)
        ↓
Notion DB에 저장 (요약·난이도·추천도·분류·저장일 등)
```

---

## 카테고리 구성

매일 아래 4개 카테고리에서 랜덤으로 키워드를 골라 총 6개를 수집합니다.

| 카테고리          | 수집 개수 | 예시 키워드                                       |
| ----------------- | --------- | ------------------------------------------------- |
| 백엔드 기본기     | 2         | spring boot, java backend, rest api, jpa          |
| 실무 감각         | 1         | spring security jwt, docker, github actions, test |
| 새로운 기술/AI    | 2         | spring ai, langchain4j, rag, mcp server, ai agent |
| 프로젝트 아이디어 | 1         | spring boot project, backend project, full stack  |

---

## 기술 스택

| 구분         | 사용 기술                                 |
| ------------ | ----------------------------------------- |
| 언어         | Python 3                                  |
| 자료 수집    | GitHub REST API                           |
| AI 요약·판단 | Google Gemini API (gemini-2.5-flash-lite) |
| 저장         | Notion API                                |
| 자동 실행    | macOS launchd (StartCalendarInterval)     |
| 라이브러리   | requests, google-genai                    |

---

## 실행 방법

### 1. 라이브러리 설치

```bash
pip3 install requests google-genai
```

### 2. config.py 작성 (비밀 정보)

```python
NOTION_TOKEN = "노션 토큰"
DATABASE_ID = "노션 DB ID"
GEMINI_KEY = "Gemini API 키"
```

> `config.py`는 `.gitignore`로 제외되어 GitHub에 올라가지 않습니다.

### 3. 실행

```bash
python3 curator.py
```

---

## 자동 실행 (매일 아침 7시)

macOS `launchd`를 사용합니다. `StartCalendarInterval` 옵션 덕분에,
아침 7시에 컴퓨터가 꺼져 있었어도 **켜질 때 밀린 작업을 실행**합니다.

설정 파일 위치:

```
~/Library/LaunchAgents/com.jm.github-curator.plist
```

실행 기록은 프로젝트 폴더의 `log.txt`, 에러는 `error.txt`에 남습니다.

---

## 폴더 구조

```
github-curator/
├── curator.py        # 메인: 수집 → 요약 → 저장
├── config.py         # 토큰·키 (git 제외)
├── test_notion.py    # 노션 연동 테스트
├── test_deepl.py     # DeepL 번역 테스트 (초기 실험)
├── test_gemini.py    # Gemini 요약 테스트
├── .gitignore
├── log.txt           # 실행 기록
└── error.txt         # 에러 기록
```

---

## 앞으로 할 것

- [ ] 같은 저장소 중복 저장 방지
- [ ] 추천도 낮은 저장소 자동 제외 (점수 필터)
- [ ] Spring Boot 버전으로 재구현 (백엔드 포트폴리오 확장)
