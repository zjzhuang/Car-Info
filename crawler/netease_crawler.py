#-*- coding: UTF-8 -*-

import urllib,urllib2,cookielib
import requests
from bs4 import BeautifulSoup
import sys, os
import json
import copy, collections, datetime, MySQLdb

#conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='15980ptpt',db='mysql',port=3306)
#cur=conn.cursor()

comment_field = ["brand", "series", "spec", "date", "web", "url", "good", "bad", "space", "power", "operate", "oil", "comfort", "appearance", "decoration", "worth", "bugs", "sustain", "other", "upvote", "downvote", "respond"]

comment_dict = collections.OrderedDict()	
for field in comment_field:
	comment_dict[field] = ""


reload(sys)  
sys.setdefaultencoding('utf8')   

def store_comment(web_name, record, raw_comment, file):
	# split_tag = ["【最满意的一点】", "【最不满意的一点】", "【空间】"]
	# processing raw_comment

	# just a temporary test!
	record["other"] = raw_comment

	for (key, value) in record.items():
		file.write("%s: %s\n" % (key, value))

	# store it in sql.
	return

def netease_crawler(brand, series, url_base):
	log = open("crawler_log.txt", "a")
	file_name = str(series) + ".txt"
	file = open(file_name, "a")

	web_name = u"网易汽车网"
	flag = 1
	page_num = 1
	url_comments = url_base

	while(flag):
		r = requests.get(url_comments)
		soup = BeautifulSoup(r.text, "lxml")
		print url_comments
		next_page = soup.body.select("div.commentList-main div.comment-pages .active")[0].next_sibling.next_sibling
		if next_page.get("class") == None:
			page_num += 1
			url_comments = url_base.split("/1_")[0] + "/" + str(page_num) + "_1.html"
			print "another_page, ", url_comments
		else:
			flag = 0
		
		# Find comments from a specific user.
		for item in soup.body.select("div.commentList-main > div.commentSingle"):
			# try:
				# print url_comments
				date = item.select("span.postTime")[0].text[:-3]
				print "date is: %s" % date
				record = copy.copy(comment_dict)
				record["brand"] = brand
				record["series"] = series
				record["spec"] = spec_name
				record["web"] = web_name
				record["date"] = date
				record["url"] = "product.auto.163.com" + comment_div.a["href"]

				content = ""
	   			comment_div = item.select("div.comBody")[0]
	   			print "comment is: ", comment_div.text
	   			content = comment_div.text.strip()[:-4]
	   			if comment_div.text[-7:-4] == "...":
	   				r = requests.get(record["url"])
	   				soup = BeautifulSoup(r.text, "lxml")
	   				content = soup.select("div.d3").text.strip()

	   			record["respond"] = respond = item.select("li.reply")[0].text[3:-1]
	   			record["upvote"] = upvote = item.select("li.useful")[0].text[3:-1]
	   			record["downvote"] = downvote = item.select("li.unuseful")[0].text[3:-1]
	   			print "respond is %s" % respond
	   			print "upvote is %s" % upvote
	   			print "downvote is %s" % downvote

	   			store_comment(web_name, record, content.strip(), file)
	   			
			# except Exception as e:
			# 	print url_comments
   #              print e
   #              log.write("Error when crawling page: " + url_comments + "\n\n")

	file.close()
	log.close()
	# print html

def main():
	# just a temperary name. Will change later.
	series = u"宝马3系"
	brand = u"宝马"
	dir = os.getcwd() + "/data/"
	if not os.path.exists("data/"):
		os.makedirs("data/")
	os.chdir("data/")

	url_comment = "http://product.auto.163.com/opinion_more/1990/1_1.html"
	netease_crawler(brand, series, url_comment)

main()
