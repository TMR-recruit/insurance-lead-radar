import os
import json
import urllib.request
import urllib.parse

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

# 최근 Telegram 메시지 가져오기
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode())

if not data["ok"] or not data["result"]:
    print("Telegram에서 받은 메시지가 없습니다.")
    print("먼저 봇에게 아무 메시지나 보내주세요.")
    exit()

# 가장 최근 메시지의 chat_id
latest = data["result"][-1]
chat_id = latest["message"]["chat"]["id"]

print("CHAT_ID 확인:", chat_id)

# 테스트 메시지 보내기
message = "🚨 보험 문의 감지 테스트입니다!\n\n알림 시스템 연결 성공 🎉"

send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

params = urllib.parse.urlencode({
    "chat_id": chat_id,
    "text": message
}).encode()

request = urllib.request.Request(send_url, data=params)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read().decode())

if result["ok"]:
    print("✅ Telegram 테스트 메시지 전송 성공!")
else:
    print("❌ 메시지 전송 실패:", result)
