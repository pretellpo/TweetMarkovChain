# -*- coding:utf-8 -*-
import json
import requests
from requests_oauthlib import OAuth1Session
import settings
import shelve
import sys

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
url_show = "https://api.twitter.com/1.1/users/show.json"

if since_id != 0:	# since_idがあるなら差分だけ取得
	params = {'screen_name': TARGET, "count": 200, "exclude_replies":True, "since_id": since_id}
	exist_tweet = len(tweet)
	new_tweet = 0
	error_tweet = 0
	napp_tweet = 0
	req_result = twitter.get(url_timeline, params=params)
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
else:	# since_idがない（新規）なら3200ツイートまで掘り返す
	exist_tweet = 0
	new_tweet = 0
	error_tweet = 0
	napp_tweet = 0

	# 総ツイート数を取得
	params = {"screen_name": TARGET}
	req_result_show = twitter.get(url_show, params=params)
	if req_result_show.status_code == 200:
		user = json.loads(req_result_show.text)
		statuses_count = user["statuses_count"]
		max_id = user["status"]["id"] + 1 # max_idを暫定的に最新ツイート+1にする
	else:
		print("ERROR: %d" % req_result_show.status_code)
		sys.exit()

	# ループ回数を計算
	tweets = min(3200,statuses_count)
	roop = tweets // 200
	if (tweets % 200) != 0:
		roop += 1

	# ツイート内容を取得
	for i in range(roop):
		params = {'screen_name': TARGET, "count": 200, "exclude_replies":True, "max_id": max_id}
		req_result_tl = twitter.get(url_timeline, params=params)
		if req_result_tl.status_code == 200:
			user_timeline = json.loads(req_result_tl.text)
			for i in user_timeline:
				if max_id > i["id"]:
					max_id = i["id"]	# max_idを古いものに更新していく
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
			print("ERROR: %d" % req_result_tl.status_code)
			sys.exit()
	


exdata["tweet"] = tweet
exdata["since_id"] = since_id
exdata.close()

print("既存ツイート:",exist_tweet,"件")
print("新規ツイート:",new_tweet,"件")
print("対象外ツイート:",napp_tweet,"件")
print("登録エラー:",error_tweet,"件")