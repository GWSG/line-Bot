# 匯入必要的模組
from flask import Flask, request, jsonify  # Flask 框架，用於啟動 Web 伺服器
import requests  # 發送 HTTP 請求的模組
import json  # 處理 JSON 格式數據的模組
from googletrans import Translator  # Google 翻譯模組

# 建立 Flask 應用程式
app = Flask(__name__)  # 初始化 Flask 伺服器應用

# LINE Bot 權杖，用於授權 LINE Messaging API
CHANNEL_ACCESS_TOKEN = "xgHW/qiMgDYqyU9zzgcpHUDNLX8pKc/5Ed+zmyePaZcvWMUlDzAP8DTqWJZ/vk1XtzswTdG9FqGp4G7Hebukm2TQhVY/jDa73QGpcPElz2lsVJyXz4YoD7k9Z0L43YaVPl7HhE9GR8/pbdzVSXZEBAdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "e626e0005ab1dc042d400b2457132663"

# 初始化 Google 翻譯器，用於翻譯訊息
translator = Translator()

# 支援語言對應表：儲存目標語言名稱與其對應的語言代碼
language_mapping = {
    "英文": "en", "English": "en",  # 英文
    "日文": "ja", "Japanese": "ja", "日本語": "ja",  # 日文
    "韓文": "ko", "Korean": "ko", "한국어": "ko", "韓國語": "ko",  # 韓文
    "中文": "zh-TW", "Chinese": "zh-TW", "繁體中文": "zh-TW",  # 繁體中文
    "越南文": "vi", "Vietnamese": "vi", "Tiếng Việt": "vi",  # 越南文
    "菲律賓文": "tl", "Tagalog": "tl", "Filipino": "tl"  # 菲律賓文 (塔加洛語)
}

# 多語言指令對應表：支援不同語言的「翻譯到」指令
translation_commands = {
    "翻譯到": "zh-TW",     # 中文
    "translate to": "en",  # 英文
    "翻訳する": "ja",       # 日文
    "번역하다": "ko",       # 韓文
    "dịch sang": "vi",     # 越南文
    "isalin sa": "tl"      # 菲律賓文 (塔加洛語)
}

# Webhook 路徑，接收來自 LINE 的 HTTP POST 請求
@app.route("/callback", methods=["POST"])
def callback():
    """
    LINE 平台的 Webhook 路徑，接收事件並進行處理。
    """
    # 取得來自 LINE 平台的請求內容
    body = request.get_data(as_text=True)
    try:
        # 將請求內容解析為 JSON 格式
        events = json.loads(body).get("events", [])  # 取得事件列表
        # 遍歷所有事件，判斷是否為文字訊息
        for event in events:
            if event.get("type") == "message" and event["message"]["type"] == "text":
                handle_message(event)  # 處理訊息
    except Exception as e:
        # 如果發生錯誤，輸出錯誤訊息
        print(f"錯誤: {e}")
    return "OK"  # 回傳成功

def handle_message(event):
    """
    處理使用者傳送的文字訊息，解析並翻譯內容。
    """
    # 從事件中取得 replyToken 和使用者訊息
    reply_token = event["replyToken"]
    user_message = event["message"]["text"]

    # 嘗試解析使用者輸入的翻譯指令
    target_language, text_to_translate = parse_translation_command(user_message)

    if target_language and text_to_translate:
        # 執行翻譯
        translated_text = translator.translate(text_to_translate, dest=target_language).text
        # 組合回覆訊息
        reply_message = (
            f"🌍 原文: {text_to_translate}\n"
            f"📄 目標語言: {get_language_name(target_language)}\n"
            f"🔄 翻譯結果: {translated_text}"
        )
    else:
        # 如果未匹配到指令，顯示公告與說明
        announcement = (
            "📢 公告：本系統支援多語言翻譯功能，讓您能輕鬆翻譯內容！\n"
            "支援語言包括：中文、英文、日文、韓文、越南文、菲律賓文等。\n"
            "請依照下方格式進行操作：\n"
        )
        reply_message = (
            f"{announcement}"
            "請使用以下格式進行翻譯：\n"
            "- 中文: 翻譯到 [語言] [內容]\n"
            "- 英文: translate to [language] [content]\n"
            "- 日文: 翻訳する [言語] [内容]\n"
            "- 韓文: 번역하다 [언어] [內容]\n"
            "- 越南文: dịch sang [ngôn ngữ] [nội dung]\n"
            "- 菲律賓文: isalin sa [wika] [nilalaman]\n"
            "例如：\n翻譯到 英文 你好\ntranslate to Vietnamese Hello\ndịch sang Filipino Kamusta"
        )

    # 發送回覆訊息
    send_reply_message(reply_token, reply_message)

def parse_translation_command(message):
    """
    解析使用者輸入，提取目標語言和翻譯內容。
    """
    # 遍歷所有支援的翻譯指令
    for command in translation_commands.keys():
        if message.lower().startswith(command.lower()):  # 確認訊息是否以指令開頭
            parts = message[len(command):].strip().split(" ", 1)  # 分割出語言和內容
            if len(parts) == 2:
                target_language_name, text_to_translate = parts
                # 從語言對應表中查找語言代碼
                for name, code in language_mapping.items():
                    if target_language_name.lower() == name.lower():
                        return code, text_to_translate
    return None, None  # 未找到指令時回傳 None

def send_reply_message(reply_token, message):
    """
    使用 LINE Messaging API 發送回覆訊息。
    """
    url = "https://api.line.me/v2/bot/message/reply"  # LINE 回覆訊息 API
    headers = {
        "Content-Type": "application/json",  # 請求格式為 JSON
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",  # 授權 Token
    }
    payload = {
        "replyToken": reply_token,  # 使用者回覆 Token
        "messages": [{"type": "text", "text": message}],  # 回傳的文字內容
    }
    # 發送 HTTP POST 請求
    response = requests.post(url, headers=headers, json=payload)
    print(f"回覆結果: {response.status_code}, {response.text}")  # 輸出回覆結果

def get_language_name(lang_code):
    """
    根據語言代碼返回語言名稱。
    """
    for name, code in language_mapping.items():
        if code == lang_code:
            return name
    return lang_code  # 如果找不到，直接回傳語言代碼

# 啟動 Flask 伺服器，監聽 5000 埠，並啟用 Debug 模式
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
