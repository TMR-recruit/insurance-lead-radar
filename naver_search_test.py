import os
import json
import urllib.request
import urllib.parse
import urllib.error
import re

CLIENT_ID = os.environ["NAVER_CLIENT_ID"]
CLIENT_SECRET = os.environ["NAVER_CLIENT_SECRET"]

QUERY = "보험료"
DISPLAY = 10

BASE_URL = "https://naverapihub.apigw.ntruss.com"


def clean_html(text):
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text)


def naver_search(api_path):
    query = urllib.parse.quote(QUERY)

    url = (
        f"{BASE_URL}{api_path}"
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
        print(f"\n❌ HTTP 오류: {e.code}")

        try:
            error_body = e.read().decode("utf-8")
            print("네이버 응답:")
            print(error_body)
        except Exception:
            pass

        raise


print("===================================")
print("NAVER API HUB 검색 테스트")
print("검색어:", QUERY)
print("===================================")


# ---------------------------------
# 1. 네이버 카페 검색
# ---------------------------------

print("\n\n========== 네이버 카페 ==========")

cafe_data = naver_search("/search/v1/cafearticle")

cafe_items = cafe_data.get("items", [])

print("검색 결과:", len(cafe_items), "개")

for i, item in enumerate(cafe_items, 1):
    print(f"\n[{i}]")
    print("제목:", clean_html(item.get("title", "")))
    print("링크:", item.get("link", ""))
    print("카페:", item.get("cafename", ""))
    print("내용:", clean_html(item.get("description", "")))


# ---------------------------------
# 2. 네이버 블로그 검색
# ---------------------------------

print("\n\n========== 네이버 블로그 ==========")

blog_data = naver_search("/search/v1/blog")

blog_items = blog_data.get("items", [])

print("검색 결과:", len(blog_items), "개")

for i, item in enumerate(blog_items, 1):
    print(f"\n[{i}]")
    print("제목:", clean_html(item.get("title", "")))
    print("링크:", item.get("link", ""))
    print("작성자:", item.get("bloggername", ""))
    print("작성일:", item.get("postdate", ""))
    print("내용:", clean_html(item.get("description", "")))


print("\n===================================")
print("✅ NAVER API HUB 검색 테스트 완료")
print("===================================")
