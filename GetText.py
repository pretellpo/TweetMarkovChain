# -*- coding:utf-8 -*-
import json
import requests
from requests_oauthlib import OAuth1Session
import settings
import shelve

# setting.pyから読み込み
CONSUMER_KEY = settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET
ACCESS_TOKEN = settings.ACCESS_TOKEN
ACCESS_TOKEN_SECRET = settings.ACCESS_TOKEN_SECRET
TARGET = settings.TARGET	# 対象のアカウント
UPPER = settings.UPPER	# ツイートの保存上限

# Twitter
twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET,
                        ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Shelveでデータを管理
exdata = shelve.open("Markov")
try:
	since_id = exdata["since_id"]
except:
	since_id = 0	# なければ0で作る
try:
	tweet = exdata["tweet"]
except:
	tweet = []

# 保存ツイート数が設定のツイート数上限より多かったら古いやつから切り落とす
if len(tweet) > UPPER:
	roop = len(tweet) - UPPER
	for i in range(roop):
		del tweet[0]

url_timeline = "https://api.twitter.com/1.1/statuses/user_timeline.json"
if since_id != 0:	# 新規かそうでないかでsince_idを使うかどうか変える（0じゃうまくいかなかった）
	params = {'screen_name': TARGET, "count": 200, "exclude_replies":True, "since_id": since_id}
else:
	params = {'screen_name': TARGET, "count": 200, "exclude_replies":True}
	
req_result = twitter.get(url_timeline, params=params)

exist_tweet = len(tweet)
new_tweet = 0
error_tweet = 0
napp_tweet = 0
if req_result.status_code == 200:
	user_timeline = json.loads(req_result.text)
	for i in user_timeline:
		if since_id < i["id"]:
			since_id = i["id"]
		try:
			text = i["text"]
			if "\n" not in text and "http" not in text and "#" not in text and "RT" not in text:	# 怪しいやつは全部弾く
				tweet.append(text)
				if len(tweet) > UPPER:
					del tweet[0]	# 保存ツイート数が上限に達していたら古いやつから削除
				new_tweet += 1
			else:
				napp_tweet += 1
		except:
			error_tweet += 1
else:
	print("ERROR: %d" % req_result.status_code)

exdata["tweet"] = tweet
exdata["since_id"] = since_id
exdata.close()

print("既存ツイート:",exist_tweet,"件")
print("新規ツイート:",new_tweet,"件")
print("対象外ツイート:",napp_tweet,"件")
print("登録エラー:",error_tweet,"件")