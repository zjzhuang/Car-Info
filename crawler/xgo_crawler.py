#-*- coding: UTF-8 -*-

import urllib,urllib2,cookielib
import requests
from bs4 import BeautifulSoup
import sys, os
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
	# processing raw_comment
	record["other"] = raw_comment

	# write in file.
	for (key, value) in record.items():
		file.write("%s: %s\n" % (key, value))

	# store it in sql.
	#sql = "insert into comments values " + str(tuple(record.values())) + ";"
	#result = cur.execute(sql)
	#conn.commit()
	return

def xgo_crawler(brand, series, url_base):
	log = open("crawler_log.txt", "a")
	file_name = str(series) + ".txt"
	file = open(file_name, "a")

	web_name = u"汽车点评网"
	flag = 1
	page_num = 1
	url_comments = url_base

	spec_name = ""
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

			record = copy.copy(comment_dict)
			record["brand"] = brand
			record["series"] = series
			record["spec"] = spec_name
			record["web"] = web_name
			
			try:
	   			comment_div = item.select("dd.paragraph div.clearfix")
				record["date"] = item.select("dd.title span.r")[0].text[4:].encode("utf-8")
				print record["date"]
				content = ""
	   			for comment_item in comment_div:
					content += comment_item.text.strip()
				# print content						
				
				info_list = tuple(i.text.encode("utf-8") for i in item.select("div.apply span.redc00"))

				record["url"] = "www.xgo.com.cn" + item.select("div.apply > a")[0]["href"]
				print "url is: ", record["url"]
				record["respond"] = info_list[0]
				record["upvote"] = info_list[1]
				record["downvote"] = info_list[2]

				store_comment(web_name, record, content.encode("utf-8"), file)

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
	series = u"宝马3系"
	brand = u"宝马"
	dir = os.getcwd() + "/data/"
	if not os.path.exists("data/"):
		os.makedirs("data/")
	os.chdir("data/")

	# xgo has no detailed classification.
	url_comment = "http://www.xgo.com.cn/2710/list_s1_p1.html"
	xgo_crawler(brand, series, url_comment)

	#cur.close()
	#conn.close()

main()
