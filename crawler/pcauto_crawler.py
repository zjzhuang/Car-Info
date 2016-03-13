#-*- coding: UTF-8 -*-

import urllib,urllib2,cookielib
import requests
from bs4 import BeautifulSoup
import sys, os
import json
import copy, collections, datetime, MySQLdb

reload(sys)  
sys.setdefaultencoding('utf8')   

conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='15980ptpt',db='mysql',port=3306)
cur=conn.cursor()

comment_field = ["brand", "series", "spec", "date", "web", "good", "bad", "space", "power", "operate", "oil", "comfort", "appearance", "decoration", "worth", "bugs", "sustain", "other", "upvote", "downvote", "respond"]

comment_dict = collections.OrderedDict()	
for field in comment_field:
	comment_dict[field] = ""

def crawl_comment(web_name, brand, series, spec_name, url_base):

	log = open("crawler_log.txt", "a")
	
	files = os.listdir(dir)
	file_name = series + ".txt"

	has_file = 0
	for name in files:
		if name.find(spec_name) != -1 and name.find("basic") == -1:
			file_name = name
			has_file = 1
			break
	if not has_file:
		return
	file = open(file_name, "a")
	file.write("**comments from pcauto\n\n\n")
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
				comment = item.select("div.table_text")[0]
				date = item.select("div.info p a")[0].text[:-2]
				print "date is: %s" % date
				upvote = item.select("a.good em")[0].text[1:-1]
				print "upvote is: %s" % upvote
				respond_script = item.select("a.answer")[0].next_sibling.text
				respond_url_pre = respond_script.split(",")[0][12:-2] 
				respond_url_next = respond_script.split(",")[1][1:-1]
				respond = json.dumps(requests.get(respond_url_pre + "&" + respond_url_next)).total
				print "respond is: %s" % respond

				# print "text:", comment.text.strip()
				for tag in comment.find_all("strong"):
					tag.string = "[" + tag.string[0:-1] + "]"
					# print tag.text.encode("utf-8")	
				file.write("from: %s\nbrand: %s\nseries: %s\nspec: %s\ndate: %s\ncontent: " % (web_name, brand, series, spec_name, date))

				file.write("comment: " + comment.text.strip() + "\n")
				for add_on in item.select("div.zjdp"):
					# note that this date is additional on original one!! e.g.: 2014-10-23 + 56 = 2014-11-23 + 26 (day!)
					add_date = item.select("div.sp2")[0].text[6:-3]
					print "additional_date: %s" % add_date
					file.write("add-on: " + add_on.select("div.zjdp_text").text  + "\n")
				file.write("upvote: " + upvote + "\n")
				file.write("respond: " + respond + "\n")
				file.write("\n\n\n")
			except Exception as e:
                                print e
                                log.write("Error when crawling page: " + url_comments + "\n\n")

	file.close()
 	log.close()

def main():
	# just a temperary name. Will change later.
	series = "66"
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
		crawl_comment("pcauto", "baoma", series, spec_name, url_comment)

	cur.close()
	conn.close()

main()
