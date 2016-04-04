#-*- coding: UTF-8 -*-

import urllib,urllib2,cookielib
import requests
from bs4 import BeautifulSoup
import sys, os
import json
import copy, collections, datetime, MySQLdb

reload(sys)  
sys.setdefaultencoding('utf8')   

#conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='15980ptpt',db='mysql',port=3306)
#cur=conn.cursor()

comment_field = ["brand", "series", "spec", "date", "web", "url", "good", "bad", "space", "power", "operate", "oil", "comfort", "appearance", "decoration", "worth", "bugs", "sustain", "other", "upvote", "downvote", "respond"]

comment_dict = collections.OrderedDict()	
for field in comment_field:
	comment_dict[field] = ""


def store_comment(web_name, record, raw_comment, file):
	split_tag = ["【最满意的一点】", "【最不满意的一点】", "【空间】"]
	# processing raw_comment

	# just a temporary test!
	record["other"] = raw_comment

	for (key, value) in record.items():
		file.write("%s: %s\n" % (key, value))

	# store it in sql.
	return


def pcauto_crawler(brand, series, url_base):
	log = open("crawler_log.txt", "a")
	file_name = series + ".txt"
	file = open(file_name, "a")

	web_name = u"太平洋汽车网"
	flag = 1
	page_num = 1
	url_comments = url_base
	while(flag):
		r = requests.get(url_comments)
		soup = BeautifulSoup(r.text, "lxml")
		has_next_page = soup.select("#pcauto_page a.next") != []
		if has_next_page:
			page_num += 1
			url_comments = url_base.split("/p"+str(page_num-1))[0] + "/p" + str(page_num) + ".html"
			print "another_page, ", page_num
		else:
			flag = 0
			
		for item in soup.select("div.main_table"):
			try:
				record = copy.copy(comment_dict)
				record["brand"] = brand
				record["series"] = series
				record["spec"] = "".join(item.select("div.car span.td2")[0].text.split())
				print "spec: ", record["spec_name"]
				record["web"] = web_name
				record["url"] = item.select("div.info > p a")[0]["href"]
				print "url: ", record["url"]

				comment = item.select("div.table_text")[0]
				record["date"] = date = item.select("div.info p a")[0].text.strip()[:-2]
				record["upvote"] = upvote = item.select("a.good em")[0].text.strip()[1:-1]
				print "date is: %s" % date
				print "upvote is: %s" % upvote

				respond_script = item.select("div.corners script")[-1].text.strip()
				respond_url_pre = respond_script.split("(")[1].split(",")[0].strip()[1:-2] 
				respond_url_next = respond_script.split(",")[1].strip()[1:-1]
				#r = requests.get(respond_url_pre + "&" + respond_url_next)
				#print respond_url_pre + "&" + respond_url_next
				#record["respond"] = respond = json.dumps(requests.get(respond_url_pre + "&" + respond_url_next).text).total
				#print "respond is: %s" % respond

				for tag in comment.find_all("strong"):
					tag.string = "[" + tag.string[0:-1] + "]"

				store_comment(web_name, record, comment.text.strip(), file)
				for add_on in item.select("div.zjdp"):
					# note that this date is additional on original one!! e.g.: 2014-10-23 + 56 = 2014-11-23 + 26 (day!)
					add_date = item.select("div.sp2")[0].text.strip()[6:-3]
					# need to convert it!
					# record["date"] = ...
					print "additional_date: %s" % add_date
					store_comment(web_name, record, add_on.select("div.zjdp_text").text.strip(), file)
					# file.write("add-on: " + add_on.select("div.zjdp_text").text  + "\n")

			except Exception as e:
				print e
				log.write("Error when crawling page: " + url_comments + "\n\n")

	file.close()
 	log.close()

def main():
	# just a temperary name. Will change later.
	series = u"宝马3系"
	brand = u"宝马"
	dir = os.getcwd() + "/data/"
	if not os.path.exists("data/"):
		os.makedirs("data/")
	os.chdir("data/")
	# to crawl a car series.
	url_series = "http://price.pcauto.com.cn/comment/sg424/"
	
	r = requests.get(url_series)

	soup = BeautifulSoup(r.text, "lxml")
	
	url_comment = "http://price.pcauto.com.cn/comment/sg424/t1/p1.html"
	pcauto_crawler(brand, series, url_comment)

	#cur.close()
	#conn.close()

main()
