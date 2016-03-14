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

comment_field = ["brand", "series", "spec", "date", "web", "good", "bad", "space", "power", "operate", "oil", "comfort", "appearance", "decoration", "worth", "bugs", "sustain", "other", "upvote", "downvote", "respond"]

comment_dict = collections.OrderedDict()	
for field in comment_field:
	comment_dict[field] = ""


def store_comment(record, raw_comment, file):
	split_tag = ["【最满意的一点】", "【最不满意的一点】", "【空间】"]
	# processing raw_comment

	# just a temporary test!
	record["other"] = raw_comment

	for (key, value) in record.items():
		file.write("%s: %s\n" % (key, value))

	# store it in sql.
	return


def crawl_comment(web_name, brand, series, spec_name, url_base):

	log = open("crawler_log.txt", "a")
	file_name = series + ".txt"
	file = open(file_name, "a")

	flag = 1
	url_comments = url_base
	page_num = 1
	while(flag):
		r = requests.get(url_comments)
		soup = BeautifulSoup(r.text, "lxml")
		has_next_page = soup.select("#pcauto_page a.next") != []
		if has_next_page:
			page_num += 1
			url_comments = url_base + "p" + str(page_num) + ".html"
			print "another_page, ", page_num
		else:
			flag = 0
			
		for item in soup.select("div.main_table"):
			try:
				record = copy.copy(comment_dict)
				record["brand"] = brand
				record["series"] = series
				record["spec"] = spec_name
				record["web"] = web_name

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

				# print "text:", comment.text.strip()
				for tag in comment.find_all("strong"):
					tag.string = "[" + tag.string[0:-1] + "]"
					# print tag.text.encode("utf-8")	
				store_comment(record, comment.text.strip(), file)
				for add_on in item.select("div.zjdp"):
					# note that this date is additional on original one!! e.g.: 2014-10-23 + 56 = 2014-11-23 + 26 (day!)
					add_date = item.select("div.sp2")[0].text.strip()[6:-3]
					# need to convert it!
					# record["date"] = ...
					print "additional_date: %s" % add_date
					store_comment(record, add_on.select("div.zjdp_text").text.strip(), file)
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
	
	# Note that it only crawls those specs which are currently sold.
	for item in soup.select("#cxList div.tr"):		
		# find a certain spec
		print "processing ..."
		url_comment = item.find("a").get("href")
		spec_name = "".join(item.find("a").text.strip().split())
		crawl_comment("pcauto", brand, series, spec_name, url_comment)

	#cur.close()
	#conn.close()

main()
