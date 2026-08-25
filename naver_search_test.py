import os
import json
import urllib.request
import urllib.parse

CLIENT_ID = os.environ["NAVER_CLIENT_ID"]
CLIENT_SECRET = os.environ["NAVER_CLIENT_SECRET"]

query = urllib.parse.quote("보험료")

url = f"https://openapi.naver.com/v1/search/cafearticle.json?query={query}&display=10&sort=date"

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id", CLIENT_ID)
request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)

with urllib.request.urlopen(request) as response:
    data = json.loads(response.read().decode("utf-8"))

print("===================================")
print("네이버 카페 검색 테스트")
print("검색어: 보험료")
print("===================================")

if "items" not in data or not data["items"]:
    print("검색 결과가 없습니다.")
else:
    for i, item in enumerate(data["items"], 1):
        print(f"\n[{i}]")
        print("제목:", item["title"])
        print("링크:", item["link"])
        print("작성일:", item.get("postdate", ""))
