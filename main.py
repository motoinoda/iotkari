from flask import Flask, request, abort
import paho.mqtt.publish as publish
import os
import json

from linebot import (
	LineBotApi, WebhookHandler
)
from linebot.exceptions import (
	InvalidSignatureError
)
from linebot.models import (
	MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

# LINE API関係の設定値取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

# Beebotte関係の設定値取得
YOUR_BEEBOTTE_TOKEN = os.environ['YOUR_BEEBOTTE_TOKEN']

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# 動作を起こすメッセージのリスト
f_msg = [s.encode('utf-8') for s in ['On']]
b_msg = [s.encode('utf-8') for s in ['Off']]
l_msg = [s.encode('utf-8') for s in ['3']]
r_msg = [s.encode('utf-8') for s in ['4']]
s_msg = [s.encode('utf-8') for s in ['5']]


# LINEに通知メッセージを送る
def broadcast_line_msg(msg):
	line_bot_api.broadcast(TextSendMessage(text=msg))

# エアコン制御用のMQTTをパブリッシュする
def publish_aircon_control_msg(msg):
	publish.single('iotkari/motor_control', \
		msg, \
		hostname='mqtt.beebotte.com', \
		port=8883, \
		auth = {'username':'token:{}'.format(YOUR_BEEBOTTE_TOKEN)}, \
		tls={'ca_certs':'mqtt.beebotte.com.pem'})

@app.route('/callback', methods=['POST'])
def callback():
	# get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']

	# get request body as text
	body = request.get_data(as_text=True)
	app.logger.info('Request body: ' + body)

	# handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)

	return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

	
	msg = event.message.text.encode('utf-8')
	if msg in f_msg:
		line_bot_api.reply_message(event.reply_token,TextSendMessage(text='ledつける'))
		publish_aircon_control_msg('1')
	elif msg in b_msg:
		line_bot_api.reply_message(event.reply_token,TextSendMessage(text='led消す'))
		publish_aircon_control_msg('2')
	elif msg in l_msg:
		publish_aircon_control_msg('3')
	elif msg in r_msg:
		publish_aircon_control_msg('4') 
	elif msg in s_msg:
		publish_aircon_control_msg('5') 
	


if __name__ == '__main__':
	port = int(os.getenv('PORT'))
	app.run(host='0.0.0.0', port=port)
