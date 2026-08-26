import os
import json
import urllib.request
import urllib.parse
import urllib.error
import re
from pathlib import Path

# ==========================================
# 설정
# ==========================================

CLIENT_ID = os.environ["NAVER_CLIENT_ID"]
CLIENT_SECRET = os.environ["NAVER_CLIENT_SECRET"]

BASE_URL = "https://naverapihub.apigw.ntruss.com"

SEARCH_KEYWORDS = [
    "보험 상담",
    "보험 추천",
    "보험 비교",
    "보험 리모델링",
    "보험 가입",
    "암보험",
    "건강보험",
    "실손보험",
    "종합보험",
    "어린이보험",
]

DISPLAY = 10

# GitHub Actions에서 계속 유지할 기록 파일
SEEN_FILE = Path("seen_posts.json")


# ==========================================
# HTML 태그 제거
# ==========================================

def clean_html(text):
    if not text:
        return ""

    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&quot;", '"')
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&amp;", "&")

    return text.strip()


# ==========================================
# 네이버 카페 검색
# ==========================================

def naver_search(keyword):

    query = urllib.parse.quote(keyword)

    url = (
        f"{BASE_URL}/search/v1/cafearticle"
        f"?query={query}"
        f"&display={DISPLAY}"
        f"&sort=date"
        f"&format=json"
    )

    request = urllib.request.Request(url)

    request.add_header(
        "X-NCP-APIGW-API-KEY-ID",
        CLIENT_ID
    )

    request.add_header(
        "X-NCP-APIGW-API-KEY",
        CLIENT_SECRET
    )

    try:

        with urllib.request.urlopen(request) as response:

            return json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as e:

        print(f"❌ 네이버 API 오류: {e.code}")

        try:
            print(
                e.read().decode("utf-8")
            )
        except Exception:
            pass

        return {"items": []}


# ==========================================
# 기존에 본 글 불러오기
# ==========================================

def load_seen():

    if not SEEN_FILE.exists():
        return set()

    try:

        with open(
            SEEN_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

            return set(data)

    except Exception:

        return set()


# ==========================================
# 본 글 저장
# ==========================================

def save_seen(seen):

    with open(
        SEEN_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            list(seen),
            f,
            ensure_ascii=False,
            indent=2
        )


# ==========================================
# 메인
# ==========================================

print("===================================")
print("🔥 보험 문의 레이더")
print("===================================")

seen = load_seen()

print(
    "현재까지 확인한 글:",
    len(seen),
    "개"
)

new_posts = []


# ==========================================
# 검색어별 검색
# ==========================================

for keyword in SEARCH_KEYWORDS:

    print(
        f"\n🔎 검색:",
        keyword
    )

    data = naver_search(keyword)

    items = data.get(
        "items",
        []
    )

    print(
        "검색 결과:",
        len(items)
    )

    for item in items:

        link = item.get(
            "link",
            ""
        )

        if not link:
            continue

        # 이미 확인한 글이면 무시
        if link in seen:
            continue

        title = clean_html(
            item.get(
                "title",
                ""
            )
        )

        description = clean_html(
            item.get(
                "description",
                ""
            )
        )

        cafe_name = item.get(
            "cafename",
            ""
        )

        post = {
            "keyword": keyword,
            "title": title,
            "link": link,
            "description": description,
            "cafename": cafe_name,
        }

        new_posts.append(post)

        # 확인한 글로 기록
        seen.add(link)


# ==========================================
# 결과 출력
# ==========================================

print("\n===================================")
print(
    "🆕 새 글:",
    len(new_posts),
    "개"
)
print("===================================")


for i, post in enumerate(
    new_posts,
    1
):

    print(
        f"\n[{i}]"
    )

    print(
        "검색어:",
        post["keyword"]
    )

    print(
        "제목:",
        post["title"]
    )

    print(
        "카페:",
        post["cafename"]
    )

    print(
        "링크:",
        post["link"]
    )

    print(
        "내용:",
        post["description"][:300]
    )


# ==========================================
# 기록 저장
# ==========================================

save_seen(seen)


print("\n===================================")
print("✅ 레이더 실행 완료")
print("===================================")
