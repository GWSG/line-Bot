from flask import Flask, request, jsonify
import requests
import json
from googletrans import Translator

# 建立 Flask 應用程式
app = Flask(__name__)

# Line Bot 權杖
CHANNEL_ACCESS_TOKEN = "xgHW/qiMgDYqyU9zzgcpHUDNLX8pKc/5Ed+zmyePaZcvWMUlDzAP8DTqWJZ/vk1XtzswTdG9FqGp4G7Hebukm2TQhVY/jDa73QGpcPElz2lsVJyXz4YoD7k9Z0L43YaVPl7HhE9GR8/pbdzVSXZEBAdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "e626e0005ab1dc042d400b2457132663"

# 初始化翻譯器
translator = Translator()

# 支援語言對應表 (目標語言名稱: 語言代碼)
language_mapping = {
    "英文": "en", "English": "en",
    "日文": "ja", "Japanese": "ja", "日本語": "ja",
    "韓文": "ko", "Korean": "ko", "한국어": "ko", "韓國語": "ko",
    "中文": "zh-TW", "Chinese": "zh-TW", "繁體中文": "zh-TW",
    "越南文": "vi", "Vietnamese": "vi", "Tiếng Việt": "vi",
    "菲律賓文": "tl", "Tagalog": "tl", "Filipino": "tl"
}

# 支援的多語言指令 (翻譯指令: 預設翻譯語言)
translation_commands = {
    "翻譯到": "zh-TW",     # 中文
    "translate to": "en",  # 英文
    "翻訳する": "ja",       # 日文
    "번역하다": "ko",       # 韓文
    "dịch sang": "vi",     # 越南文
    "isalin sa": "tl"      # 菲律賓文 (塔加洛語)
}

@app.route("/callback", methods=["POST"])
def callback():
    body = request.get_data(as_text=True)
    try:
        events = json.loads(body).get("events", [])
        for event in events:
            if event.get("type") == "message" and event["message"]["type"] == "text":
                handle_message(event)
    except Exception as e:
        print(f"錯誤: {e}")
    return "OK"

def handle_message(event):
    reply_token = event["replyToken"]
    user_message = event["message"]["text"]

    # 解析用戶輸入是否為翻譯指令
    target_language, text_to_translate = parse_translation_command(user_message)

    if target_language and text_to_translate:
        # 翻譯文本
        translated_text = translator.translate(text_to_translate, dest=target_language).text
        reply_message = (
            f"🌍 原文: {text_to_translate}\n"
            f"📄 目標語言: {get_language_name(target_language)}\n"
            f"🔄 翻譯結果: {translated_text}"
        )
    else:
        # 未匹配到翻譯指令，提供公告與說明
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
            "- 韓文: 번역하다 [언어] [내용]\n"
            "- 越南文: dịch sang [ngôn ngữ] [nội dung]\n"
            "- 菲律賓文: isalin sa [wika] [nilalaman]\n"
            "例如：\n翻譯到 英文 你好\ntranslate to Vietnamese Hello\ndịch sang Filipino Kamusta"
        )

    send_reply_message(reply_token, reply_message)

def parse_translation_command(message):
    """
    解析使用者輸入，匹配多語言翻譯指令，並提取目標語言和內容
    """
    for command in translation_commands.keys():
        if message.lower().startswith(command.lower()):
            parts = message[len(command):].strip().split(" ", 1)
            if len(parts) == 2:
                target_language_name, text_to_translate = parts
                # 嘗試匹配目標語言名稱
                for name, code in language_mapping.items():
                    if target_language_name.lower() == name.lower():
                        return code, text_to_translate
    return None, None

def send_reply_message(reply_token, message):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}],
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"回覆結果: {response.status_code}, {response.text}")

def get_language_name(lang_code):
    """
    根據語言代碼返回語言名稱
    """
    for name, code in language_mapping.items():
        if code == lang_code:
            return name
    return lang_code

# 啟動 Flask 伺服器
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
