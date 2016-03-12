#-*- coding: UTF-8 -*-

import urllib,urllib2,cookielib
import requests
from bs4 import BeautifulSoup
import sys, os
import copy, collections, datetime, MySQLdb

reload(sys)  
sys.setdefaultencoding('utf8')   


conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='15980ptpt',db='mysql',port=3306)
cur=conn.cursor()

comment_field = ["brand", "series", "spec", "date", "web", "good", "bad", "space", "power", "operate", "oil", "comfort", "appearance", "decoration", "worth", "bugs", "sustain", "other", "upvote", "downvote", "respond"]

comment_dict = collections.OrderedDict()	
for field in comment_field:
	comment_dict[field] = ""

def crawl_comment(web_name, series, url_base, spec_name = "null"):

	# open the log.
	log = open("crawler_log.txt", "a")
	
	# get the file name.
	file_name = str(series) + ".txt"

	file = open(file_name, "a")
	# file.write("**comments from xgo\n\n\n")

	flag = 1
	url_comments = url_base
	page_num = 1

	while(flag):
		r = requests.get(url_comments)
		soup = BeautifulSoup(r.text, "lxml")
		page_all = soup.body.find_all("div", class_="xgo_cars_page")
		if (page_all != [] and page_all[0].find_all("a", class_="next") != []):
			page_num += 1
			url_comments = url_base[:-6] + str(page_num) + ".html"
			print "another_page, ", url_comments
		else:
			flag = 0
		
		# Find comments from a specific user.
		for item in soup.body.select("div.xgo_cars_dianping dl.info"):

			comment = copy.copy(comment_dict)
			comment["brand"] = "baoma"
			comment["series"] = "66"
			comment["spec"] = spec_name
			comment["web"] = web_name
			
			try:
	   			comment_div = item.select("dd.paragraph div.clearfix")
				comment["date"] = item.select("dd.title span.r")[0].text[4:].encode("utf-8")

	   			record = "from: %s\nspec: %s\ndate: %s\ncontent: " % (web_name, spec_name, item.select("dd.title span.r")[0].text[4:]) 
				content = ""
	   			for comment_item in comment_div:
	   				record += comment_item.text.strip()
					content += comment_item.text.strip()
				comment["other"] = content.encode("utf-8")			
				
				info_list = tuple(i.text.encode("utf-8") for i in item.select("div.apply span.redc00"))

	   			record += "\nrespond: %s\nupvote: %s\ndownvote: %s\n\n" % info_list
				comment["respond"] = info_list[0]
				comment["upvote"] = info_list[1]
				comment["downvote"] = info_list[2]

				sql = "insert into comments values " + str(tuple(comment.values())) + ";"
				# print sql
				result = cur.execute(sql)
				conn.commit()
	   			file.write(record)
			except Exception as e:
				print url_comments
                		print e
                		log.write("Error when crawling page: " + url_comments + "\n\n")
		# cur.commit()
	file.close()
	log.close()
	# print html

def main():

	# just a temperary name. Will change later.
	series = 66
	dir = os.getcwd() + "/data/"
	if not os.path.exists("data/"):
		os.makedirs("data/")
	os.chdir("data/")

	# xgo has no detailed classification.
	url_comment = "http://www.xgo.com.cn/2710/list_s1_p1.html"
	
	crawl_comment("xgo", series, url_comment)

	cur.close()
    	conn.close()

main()
