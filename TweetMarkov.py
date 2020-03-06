# -*- coding:utf-8 -*-
import json
import requests
import MeCab
import markovify
import shelve
import settings
from requests_oauthlib import OAuth1Session

tagger = MeCab.Tagger("-Owakati")

exdata = shelve.open("Markov")
tweet = exdata["tweet"]

parsed_text = ""
for i in tweet:
	parsed_text += tagger.parse(i) + "\n"	# 1ツイート1行の文字列に変換

exdata.close()

STATE_SIZE = settings.STATE_SIZE
text_model = markovify.NewlineText(parsed_text, state_size=STATE_SIZE)	# 生成した文字列をぶっこむ

output = text_model.make_short_sentence(130,tries=100).replace(" ","") # 130文字内で生成

tweet = output + " #bot"	# 分かち書きのスペースを除去

print(output)

# 結果をツイート
CONSUMER_KEY = settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET
ACCESS_TOKEN = settings.ACCESS_TOKEN
ACCESS_TOKEN_SECRET = settings.ACCESS_TOKEN_SECRET
twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET,
                        ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
url_tweet = "https://api.twitter.com/1.1/statuses/update.json"
params = {"status": tweet}
req_result = twitter.post(url_tweet ,params = params)
if req_result.status_code != 200:
	print("ERROR: %d" % req_result.status_code)