import os
import json
import urllib.request
import urllib.parse
import urllib.error
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ==========================================
# 기본 설정
# ==========================================

CLIENT_ID = os.environ["NAVER_CLIENT_ID"]
CLIENT_SECRET = os.environ["NAVER_CLIENT_SECRET"]

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

BASE_URL = "https://naverapihub.apigw.ntruss.com"

DISPLAY = 10

SEEN_FILE = Path("seen_posts.json")
DISCOVERED_FILE = Path("discovered_posts.json")

KST = timezone(timedelta(hours=9))


# ==========================================
# 검색어
# ==========================================

SEARCH_KEYWORDS = [
    "보험 상담",
    "보험 추천",
    "보험 비교",
    "보험 리모델링",
    "보험 가입",
    "보험 고민",
    "보험료 부담",
    "실비보험",
    "실손보험",
    "암보험",
    "건강보험",
    "종합보험",
    "어린이보험",
    "보험료",
]


# ==========================================
# 카페명으로 제외할 키워드
# ==========================================

EXCLUDED_CAFE_KEYWORDS = [
    "보험 강의",
    "보험 금융",
]


# ==========================================
# 태아보험 관련 글 제외
# ==========================================

EXCLUDED_TEXT_KEYWORDS = [
    "태아보험",
    "태아 보험",
]


# ==========================================
# 상담 가능성을 높이는 표현
# ==========================================

POSITIVE_KEYWORDS = {

    "상담": 3,
    "추천": 2,
    "가입": 2,
    "비교": 2,
    "리모델링": 3,
    "고민": 2,
    "문의": 3,
    "궁금": 2,
    "알려주세요": 2,
    "어떻게": 2,
    "괜찮을까요": 3,
    "가능할까요": 3,
    "어떤": 1,
    "알아보": 2,
    "들어야": 2,
    "바꿔야": 2,
    "정리": 2,
    "부담": 2,
    "부족": 2,
    "없는데": 2,
    "처음": 1,
    "월": 1,
}


# ==========================================
# 광고 / 정보성 표현
# ==========================================

NEGATIVE_KEYWORDS = {

    "광고": 5,
    "이벤트": 4,
    "모집": 5,
    "홍보": 5,
    "강의": 5,
    "교육": 4,
    "설계사": 3,
    "재무설계": 3,
    "수익": 4,
    "환급": 4,
    "지원금": 4,
    "정부지원": 4,
    "최신정보": 3,
    "신청방법": 3,
    "꿀팁": 3,
    "추천상품": 3,
}


# ==========================================
# HTML 제거
# ==========================================

def clean_html(text):

    if not text:
        return ""

    text = re.sub(r"<[^>]+>", "", text)

    replacements = {
        "&quot;": '"',
        "&lt;": "<",
        "&gt;": ">",
        "&amp;": "&",
        "&#39;": "'",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

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

        print(
            f"❌ 네이버 API 오류: {e.code}"
        )

        try:
            print(
                e.read().decode("utf-8")
            )
        except Exception:
            pass

        return {"items": []}

    except Exception as e:

        print(
            "❌ 네이버 검색 오류:",
            e
        )

        return {"items": []}


# ==========================================
# 이미 본 글 불러오기
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

            return set(json.load(f))

    except Exception:

        return set()


# ==========================================
# 이미 본 글 저장
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
# 발견 시간 기록 불러오기
# ==========================================

def load_discovered():

    if not DISCOVERED_FILE.exists():
        return {}

    try:

        with open(
            DISCOVERED_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return {}


# ==========================================
# 발견 시간 기록 저장
# ==========================================

def save_discovered(data):

    with open(
        DISCOVERED_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


# ==========================================
# 카페명 제외 여부
# ==========================================

def is_excluded_cafe(cafe_name):

    cafe_name_lower = cafe_name.lower()

    for keyword in EXCLUDED_CAFE_KEYWORDS:

        if keyword.lower() in cafe_name_lower:

            return True

    return False


# ==========================================
# 태아보험 등 제외 여부
# ==========================================

def is_excluded_text(title, description):

    text = (
        title + " " + description
    ).lower()

    for keyword in EXCLUDED_TEXT_KEYWORDS:

        if keyword.lower() in text:

            return True

    return False


# ==========================================
# 상담 가능성 점수
# ==========================================

def calculate_score(
    title,
    description,
    cafe_name
):

    text = (
        title + " "
        + description + " "
        + cafe_name
    ).lower()

    score = 0

    positive_found = []
    negative_found = []

    # 긍정 키워드
    for keyword, points in POSITIVE_KEYWORDS.items():

        if keyword.lower() in text:

            score += points

            positive_found.append(
                keyword
            )

    # 부정 키워드
    for keyword, points in NEGATIVE_KEYWORDS.items():

        if keyword.lower() in text:

            score -= points

            negative_found.append(
                keyword
            )

    # 제목에 질문 형태가 있으면 가산
    if "?" in title:

        score += 2

    # 제목 자체가 질문형 표현이면 가산
    question_patterns = [
        "어떻게",
        "괜찮",
        "가능",
        "추천",
        "궁금",
        "알아보",
        "해야",
        "어떤",
        "있나요",
        "없나요",
    ]

    for pattern in question_patterns:

        if pattern in title:

            score += 2

            break

    return (
        score,
        positive_found,
        negative_found
    )


# ==========================================
# 등급
# ==========================================

def get_grade(score):

    if score >= 8:
        return "🔥 높은 가능성"

    if score >= 5:
        return "🟡 가능성 있음"

    return "⚪ 낮은 가능성"


# ==========================================
# Telegram 전송
# ==========================================

def send_telegram(message):

    if not TELEGRAM_CHAT_ID:

        print(
            "⚠️ TELEGRAM_CHAT_ID가 없습니다."
        )

        return False

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    data = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": "false"
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        method="POST"
    )

    try:

        with urllib.request.urlopen(
            request
        ) as response:

            result = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

            return result.get(
                "ok",
                False
            )

    except Exception as e:

        print(
            "❌ Telegram 전송 오류:",
            e
        )

        return False


# ==========================================
# 메인
# ==========================================

print("===================================")
print("🔥 보험 문의 레이더")
print("===================================")

now = datetime.now(KST)

discovered_time = now.strftime(
    "%Y-%m-%d %H:%M:%S"
)

print(
    "레이더 실행:",
    discovered_time
)

seen = load_seen()
discovered = load_discovered()

print(
    "기존 확인 글:",
    len(seen),
    "개"
)

new_posts = []


# ==========================================
# 검색 시작
# ==========================================

for keyword in SEARCH_KEYWORDS:

    print(
        f"\n🔎 검색: {keyword}"
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

        # 이미 확인한 글
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

        cafe_name = clean_html(
            item.get(
                "cafename",
                ""
            )
        )

        # ==================================
        # 1. 제외 카페
        # ==================================

        if is_excluded_cafe(
            cafe_name
        ):

            print(
                "  🚫 제외 카페:",
                cafe_name
            )

            seen.add(link)

            continue

        # ==================================
        # 2. 태아보험 등 제외
        # ==================================

        if is_excluded_text(
            title,
            description
        ):

            print(
                "  🚫 제외 키워드:",
                title
            )

            seen.add(link)

            continue

        # ==================================
        # 3. 점수 계산
        # ==================================

        score, positive_found, negative_found = calculate_score(
            title,
            description,
            cafe_name
        )

        grade = get_grade(score)

        print(
            f"  점수 {score}: {title}"
        )

        # ==================================
        # 4. 낮은 점수 제외
        # ==================================

        if score < 5:

            print(
                "  ⚪ 낮은 가능성 → 제외"
            )

            seen.add(link)

            continue

        # ==================================
        # 최초 발견 시간
        # ==================================

        if link not in discovered:

            discovered[link] = {
                "first_seen": discovered_time,
                "title": title,
                "cafe": cafe_name,
                "keyword": keyword,
            }

        post = {
            "keyword": keyword,
            "title": title,
            "link": link,
            "description": description,
            "cafename": cafe_name,
            "score": score,
            "grade": grade,
            "first_seen": discovered[link][
                "first_seen"
            ],
            "positive": positive_found,
            "negative": negative_found,
        }

        new_posts.append(post)

        seen.add(link)


# ==========================================
# Telegram 알림
# ==========================================

print("\n===================================")
print(
    "🔥 새 문의 후보:",
    len(new_posts),
    "개"
)
print("===================================")


for post in new_posts:

    positive_text = ", ".join(
        post["positive"][:8]
    )

    message = (
        "🚨 보험 문의 발견!\n\n"
        f"{post['grade']}\n"
        f"📊 상담 가능성 점수: {post['score']}점\n"
        f"🕐 최초 발견: {post['first_seen']}\n\n"
        f"📌 {post['title']}\n"
        f"🏠 {post['cafename']}\n"
        f"🔎 검색어: {post['keyword']}\n\n"
        f"💬 {post['description'][:600]}\n\n"
        f"🔗 {post['link']}\n\n"
        f"🔍 감지 표현: {positive_text}"
    )

    print(
        "\n📨 Telegram 전송:",
        post["title"]
    )

    success = send_telegram(
        message
    )

    if success:

        print(
            "  ✅ 전송 성공"
        )

    else:

        print(
            "  ❌ 전송 실패"
        )


# ==========================================
# 기록 저장
# ==========================================

save_seen(seen)
save_discovered(discovered)


print("\n===================================")
print("✅ 레이더 실행 완료")
print("===================================")
