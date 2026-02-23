from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

app = Flask(__name__)

configuration = Configuration(access_token='HPooPq9Qj4JhNgjvGQUtbAYltkhsxTSQT80f9hRSkTUKfVRVpHIWkKs0WAx3DRN4hYpoAVmrYNjGq3uCUOJOr3cGmawYRMA2e6hrjbsorTl+NMak93DxVDz3d6xU2/bThCmsTF2SWZrAzxAOeuwjbAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('fdb47df684d9f71ef1d0e74a9d47b021')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

from time import time 
users = {}
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    userId = event.source.user_id
    api_instance = MessagingApi(ApiClient(configuration))

    # 条件分岐
    if event.message.text == "勉強開始":
        reply_text = "計測を開始しました！"
        if userId not in users:
            users[userId] = {}  # ユーザーIDをキーにして空の辞書を作成
            users[userId]["total"] = 0  # 勉強時間の合計を初期化
        users[userId]["start"] = time()  # 勉強開始時間を記録
       
    else:
        end= time()  # 勉強終了時間を記録
        diffrence = int(end - users[userId]["start"])  # 勉強時間を計算   
        users[userId]["total"] += diffrence  # 勉強時間を合計に加算
        hour = diffrence // 3600  # 時間を計算
        minute = (diffrence % 3600) // 60  # 分を計算
        second = diffrence % 60  # 秒を計算
        reply_text = f"勉強時間は{hour}時間{minute}分{second}秒です。お疲れ様でした！本日の合計勉強時間は{hour}時間{minute}分{second}秒です。"

    # 返信メッセージ作成
    reply_message_request = ReplyMessageRequest(
        reply_token=event.reply_token,
        messages=[
            TextMessage(
                type='text',
                text=reply_text
            )
        ]
    )

    # 返信
    api_instance.reply_message(reply_message_request)

if __name__ == "__main__":
    app.run()