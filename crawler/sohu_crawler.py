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

def sohu_crawler(brand, series, url_base):
	log = open("crawler_log.txt", "a")
	file_name = str(series) + ".txt"
	file = open(file_name, "a")

	web_name = u"搜狐汽车网"
	flag = 1
	page_num = 1
	url_comments = url_base

	while(flag):
		r = requests.get(url_comments)
		soup = BeautifulSoup(r.text, "lxml")
		next_page = soup.body.select("div.pagelist_new li.bg_white")[0].previous_sibling.previous_sibling
		print next_page.attrs
		if next_page.attrs == {}: # no class named "unable"
			page_num += 1
			url_comments = url_base.split("dianping")[0] + "dianping_1_" + str(page_num) + ".html"
			print "another_page, ", url_comments
		else:
			flag = 0	
		# Find comments from a specific user.
		for item in soup.body.select("ul.pllist > li"):
			try:
				#print item
				spec_name = series + "".join(item.select("div.pltit")[0].h3.a.text.split())
				#print item.select("span.time")[0].text
				date = item.select("span.time")[0].text.split(u"发表于")[-1].text.strip()
				print "date is: %s" % date
				record = copy.copy(comment_dict)
				record["brand"] = brand
				record["series"] = series
				record["spec"] = spec_name
				record["web"] = web_name
				record["date"] = date
				record["url"] = url_comments + "#" + str(item.div["id"])
				print "url is: ", record["url"]

				content = ""
	   			comment_div = item.select("div.pltxt")[0]
	   			for tag in comment_div.select("p"):
					pair = tag.text.split()
	   				content += u"【" + pair[0] + u"】"
	   				content += pair[1] + "\n"
				#print content
	   			store_comment(web_name, record, content.strip(), file)
	   			
			except Exception as e:
				print e
				print url_comments
              			log.write("Error when crawling page: " + url_comments + "\n\n")

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

	url_comment = "http://db.auto.sohu.com/huachenbmw/1232/dianping_1.html"
	sohu_crawler(brand, series, url_comment)

main()
