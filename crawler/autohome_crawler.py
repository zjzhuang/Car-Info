#-*- coding: UTF-8 -*-

import urllib,urllib2,cookielib
import requests
from bs4 import BeautifulSoup
import sys, os
import json
import copy, collections, datetime, MySQLdb


#conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='15980ptpt',db='mysql',port=3306)
#cur=conn.cursor()

comment_field = ["brand", "series", "spec", "date", "web", "good", "bad", "space", "power", "operate", "oil", "comfort", "appearance", "decoration", "worth", "bugs", "sustain", "other", "upvote", "downvote", "respond"]

comment_dict = collections.OrderedDict()	
for field in comment_field:
	comment_dict[field] = ""

# get the pool from sql further.
url_pool = {}

reload(sys)  
sys.setdefaultencoding('utf8')   


def store_comment(record, raw_comment, file):
	split_tag = ["【最满意的一点】", "【最不满意的一点】", "【空间】"]
	# processing raw_comment

	# just a temporary test!
	record["other"] = raw_comment

	for (key, value) in record.items():
		file.write("%s: %s\n" % (key, value))

	# store it in sql.
	return

def crawl_basic(url_basic, car_id):
	r = requests.get(url_basic)
	
	configList = r.text.split("config = ")[1].split(";")[0]
	configList = json.loads(configList)
	car_name = "".join(configList["result"]["paramtypeitems"][0]["paramitems"][0]["valueitems"][0]["value"].split(" "))
	file_name = car_name.encode("utf8") + "_basic" + ".txt"
	file = open(file_name, 'w')

	# extract basic infomation.
	basic_config = {}

	for item in configList["result"]["paramtypeitems"][0]["paramitems"]:
		
		basic_config[item["name"]] = item["valueitems"][0]["value"]
		file.write("%%" + item["name"] + ":" + basic_config[item["name"]] + "\n") 

	file.close()
	return car_name

def crawl_comment(web_name, brand, series, url_base):

	log = open("crawler_log.txt", "a")
	file_name = series + ".txt"
	file = open(file_name, "a")

	flag = 1

	url_comment = url_base
	page_num = 1
	while(flag):
		r = requests.get(url_comment)
		soup = BeautifulSoup(r.text, "lxml")
		page_next = soup.body.find_all("a", class_="page-item-next")
		# No next page.
		if (page_next != [] and page_next[0].get("href") != "###"):
			page_num += 1
			url_comment = url_base + "/index_" + str(page_num) + ".html"
			# print url_comment
		else:
			flag = 0
			
		for item in soup.body.find_all("div", class_="mouthcon"):

			record = copy.copy(comment_dict)
			record["brand"] = brand
			record["series"] = series
			record["spec"] = spec_name = "".join(item.select("div.mouthcon-cont-left dl.choose-dl dd")[0].text.split())
			record["web"] = web_name

			# get the specific comment page.
			# try:
			main_comment = item.select(".mouth-main .mouth-item .text-con")[0].text.strip()

			# list of date (including real comment, add-ons.)
			date = item.select(".mouth-main .mouth-item .title-name b")
			record["date"] = date[-1].text.strip()
			print "date: ", date[-1].text
			# write additional info
			record["upvote"] = upvote = item.select(".mouth-main .mouth-remak label.supportNumber")[0].text
			record["respond"] = respond = item.select(".mouth-main .mouth-remak span.CommentNumber")[0].text
			print "upvote is " + upvote
			print "respond is " + respond
			store_comment(record, main_comment, file)
			
			# if there are no add-ons, do not need to follow on.
			if item.select("dl.add-dl") != []:
				print "follow on add-on comment"
				r = requests.get(item.select(".mouth-main .mouth-item .cont-title .title-name a")[0]["href"])
				soup = BeautifulSoup(r.text, "lxml")
				add_on_comments = item.select(".mouth-main .mouth-item")[:-1]

				for item in add_on_comments:
					add_on_comment = item.select("dd.add-dl-text")[0].text.strip()
					record["date"] = item.select("div.title-name b").text.strip() 
					store_comment(record, add_on_comment, file)
			# except Exception as e:
			# 	print e
			# 	log.write("Error when crawling page: " + str(url_comment) + "\n")

	file.close()
	log.close()

def main():
	series = u"宝马3系"
	brand = u"宝马"
	if not os.path.exists("data/"):
		os.makedirs("data/")
	os.chdir("data/")

	# get all car lists.
	url_series = "http://car.autohome.com.cn/config/series/66.html"
	r = requests.get(url_series)
	car_list_str = r.text.split("specIDs =")[1].split(";")[0]
	car_list = [int(s.strip()) for s in car_list_str[1:-1].split(",")]
	

	# for car_id in car_list:		
	# 	url_basic = "http://car.autohome.com.cn/config/spec/" + str(car_id) + ".html"
	# 	car_name = crawl_basic(url_basic, car_id)
		
	url_comment = "http://k.autohome.com.cn/66/ge0/0-0-2"
	crawl_comment("autohome", brand, series, url_comment)

	#cur.close()
	#conn.close()

main()

