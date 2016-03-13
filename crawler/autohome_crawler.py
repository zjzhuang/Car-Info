#-*- coding: UTF-8 -*-

import urllib,urllib2,cookielib
import requests
from bs4 import BeautifulSoup
import sys, os
import json
import copy, collections, datetime, MySQLdb


conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='15980ptpt',db='mysql',port=3306)
cur=conn.cursor()

comment_field = ["brand", "series", "spec", "date", "web", "good", "bad", "space", "power", "operate", "oil", "comfort", "appearance", "decoration", "worth", "bugs", "sustain", "other", "upvote", "downvote", "respond"]

comment_dict = collections.OrderedDict()	
for field in comment_field:
	comment_dict[field] = ""


reload(sys)  
sys.setdefaultencoding('utf8')   

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

def crawl_comment(web_name, series, brand, url_base, spec_name, car_id):

	split_tag = ["【最满意的一点】", "【最不满意的一点】", "【空间】"]

	log = open("crawler_log.txt", "a")

	file_name = series + ".txt"
	file = open(file_name, "a")

	# file.write("**comments from auto_home\n\n\n")
	# file.write("car_id:" + str(car_id) + "\n")
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
			record["series"] = "66"
			record["spec"] = spec_name
			record["web"] = web_name

			# get the specific comment page.
			try:
				r = requests.get(item.select(".mouth-main .mouth-item .cont-title .title-name a")[0]["href"])
			except e:
				print e
                                log.write("Error when crawling page: " + url_comment + "\ 	n Error msg: " + e + "\n\n")

			soup = BeautifulSoup(r.text, "lxml")
			# all comments including add-ons.
			
			comments = soup.select(".mouth-main .mouth-item .text-con")

			# list of date (including real comment, add-ons.)
			date = soup.select(".mouth-main .mouth-item .title-name b")
			file.write("from: %s\nbrand: %s\nseries: %s\nspec: %s\ndate: %s\ncontent: " % (web_name, brand, series, spec_name, date[-1]))

			# write real comment		
			file.write("comment: " + comments[-1].text.strip() + "\n")

			for i in range(len(comments[0:-1])-1):
				add_on = comments[i]
				# can further get data on comment_time, average_oil_per_mile etc.
				if add_on.select("dd.add-dl-text") == []:
					continue
				add_on_date = date[i]
				# write add-ons
				file.write("add-on: " + add_on.select("dd.add-dl-text")[0].text.strip() + "\n")
				# print "add_ons:", comment.select("dd.add-dl-text")[0].text
			# write additional info
			upvote = item.select(".mouth-main .mouth-remak label.supportNumber")[0].text
			respond = item.select(".mouth-main .mouth-remak span.CommentNumber")[0].text
			print "upvote is " + upvote
			print "respond is " + respond
			file.write("upvote: " + upvote + "\n")
			file.write("respond: " + respond + "\n")
	file.close()
	log.close()

def main():

	series = "66"
	if not os.path.exists("data/"):
		os.makedirs("data/")
	os.chdir("data/")

	# get all car lists.
	url_series = "http://car.autohome.com.cn/config/series/" + str(series) + ".html"
	r = requests.get(url_series)
	car_list_str = r.text.split("specIDs =")[1].split(";")[0]
	car_list = [int(s.strip()) for s in car_list_str[1:-1].split(",")]
	

	for car_id in car_list:		
		print "Processing", car_id, "..."
		url_basic = "http://car.autohome.com.cn/config/spec/" + str(car_id) + ".html"
		url_comment = "http://k.autohome.com.cn/spec/" + str(car_id)

		car_name = crawl_basic(url_basic)
		crawl_comment("autohome", "baoma", series, url_comment, car_name, car_id)

	cur.close()
	conn.close()

main()

