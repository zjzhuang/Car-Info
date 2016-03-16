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

# get the pool from sql further.
url_pool = [
	{"web": "autohome", "url": "http://k.autohome.com.cn/66/ge0/0-0-2", "last_visit": ""},
	{"web": "yiche", "url": "http://car.bitauto.com/baoma3xi/koubei/tags/%E7%BB%BC%E5%90%88/", "last_visit": ""},
	{"web": "pcauto", "url": "http://price.pcauto.com.cn/comment/sg424/t1/p1.html", "last_visit": ""},
	{"web": "xgo", "url": "http://www.xgo.com.cn/2710/list_s1_p1.html", "last_visit": ""},
	{"web": "sohu", "url": "http://db.auto.sohu.com/huachenbmw/1232/dianping_1.html", "last_visit": ""},
	{"web": "netease", "url": "http://product.auto.163.com/opinion_more/1990/1_1.html", "last_visit": ""},
]

reload(sys)  
sys.setdefaultencoding('utf8')   


def store_comment(web_name, record, raw_comment, file):
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

def autohome_crawler(brand, series, url_base):
	web_name = u"汽车之家"
	log = open("crawler_log.txt", "a")
	file_name = series + ".txt"
	file = open(file_name, "a")

	flag = 1
	page_num = 1
	url_comment = url_base
	while(flag):
		r = requests.get(url_comment)
		soup = BeautifulSoup(r.text, "lxml")
			
		for item in soup.body.find_all("div", class_="mouthcon"):
			record = copy.copy(comment_dict)
			record["brand"] = brand
			record["series"] = series
			record["spec"] = "".join(item.select("div.mouthcon-cont-left dl.choose-dl dd")[0].text.split())
			record["web"] = web_name
			record["url"] = item.select(".mouth-main .mouth-item .cont-title .title-name a")[0]["href"]

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
			store_comment(web_name, record, main_comment, file)
			
			# if there are no add-ons, do not need to follow on.
			if item.select("dl.add-dl") != []:
				r = requests.get(record["url"])
				soup = BeautifulSoup(r.text, "lxml")
				add_on_comments = item.select(".mouth-main .mouth-item")[:-1]

				for item in add_on_comments:
					add_on_comment = item.select("dd.add-dl-text")[0].text.strip()
					record["date"] = item.select("div.title-name b").text.strip() 
					store_comment(web_name, record, add_on_comment, file)
			# except Exception as e:
			# 	print e
			# 	log.write("Error when crawling page: " + str(url_comment) + "\n")
		
		page_next = soup.body.find_all("a", class_="page-item-next")
		# Get next page.
		if (page_next != [] and page_next[0].get("href") != "###"):
			page_num += 1
			url_comment = url_base + "/index_" + str(page_num) + ".html"
		else:
			flag = 0
	file.close()
	log.close()

def yiche_crawler(brand, series, url_base):
	log = open("crawler_log.txt", "a")	
	file_name = series + ".txt"
	file = open(file_name, "a")

	web_name = u"易车网"
	flag = 1
	page_num = 1
	url_comments = url_base

	while(flag):
		r = requests.get(url_comments)
		soup = BeautifulSoup(r.text, "lxml")
		
		# Find comments from a specific user.
		for item in soup.body.find_all("div", id="topiclistshow")[0].find_all("dl"):
			# try:
			spec_name = series + "".join(item.select("p.carname")[0].text.split())
			url_comment_list = item.find_all("ul", class_="cont_list")[0].find_all("li")

			# One user may have several comments.
			for url_comment in url_comment_list:
				record = copy.copy(comment_dict)
				record["brand"] = brand
				record["series"] = series
				record["spec"] = spec_name
				record["web"] = web_name
				record["url"] = url_comment.a.get("href")
				
				r = requests.get(record["url"])
				print url_comment.a.get("href")
				soup = BeautifulSoup(r.text, "lxml")

				# filter some special comments.
				if soup.select("span.fapiao_tab") != []:
					continue

				comment = soup.select("div#content_bit div.article-contents")[0]
				
				record["respond"] = respond = url_comment.select("div.rbox")[0].a.span.text[3:-1].strip()
				record["upvote"] = upvote = url_comment.select("div.rbox em")[-1].text[1:-1].strip()
				record["date"] = date = soup.select("#time")[0].text.strip()
				print "respond is: %s" % respond
				print "upvote is: %s" % upvote
				print "date is: %s" % date 

				if comment.select("p.czjg_xq_cont") != []: # which means that comment is not valid.
					continue
				# pre-process the text for convenience.
				for tag in comment.find_all("strong"):
					if not tag.string:
						continue
					tag.string = u"【" + tag.string.strip() + u"】"
					# print tag.text
				for p in comment.find_all("p"):
					if not p.string:
						continue
					p.string = p.string.strip()
				# Here we clean some data.
				if comment.h4:
					comment.h4.extract()
				if comment.pre:
					comment.pre.extract()
				if comment.find("div.con_nav2"):
					comment.find("duv.con_nav2").extract()

				store_comment(web_name, record, comment.text.strip(), file)

			# except Exception as e:
			# 	print url_comment.a.get("href")
			# 	print e
			# 	log.write("Error when crawling page: " + url_comment.a.get("href") + "\n\n")

		page_all = soup.body.find_all("span", id_="main_pager_down")
		if (page_all != [] and page_all[0].find_all("a", class_="next_on") != []):
			page_num += 1
			url_comments = url_base + "page" + str(page_num)
			print "another_page, ", page_num
		else:
			flag = 0

	file.close()
	log.close()
	# print html

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
			
		for item in soup.select("div.main_table"):
			try:
				record = copy.copy(comment_dict)
				record["brand"] = brand
				record["series"] = series
				record["spec"] = "".join(item.select("div.car span.td2")[0].text.split())
				print "spec: ", record["spec"]
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
					tag.string = u"【" + tag.string[0:-1] + u"】"
				print "comment is: ", comment.text.strip()
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

		has_next_page = soup.select("#pcauto_page a.next") != []
		if has_next_page:
			page_num += 1
			url_comments = url_base.split("/p"+str(page_num-1))[0] + "/p" + str(page_num) + ".html"
			print "another_page, ", page_num
		else:
			flag = 0

	file.close()
 	log.close()

def xgo_crawler(brand, series, url_base):
	log = open("crawler_log.txt", "a")
	file_name = series + ".txt"
	file = open(file_name, "a")

	web_name = u"汽车点评网"
	flag = 1
	page_num = 1
	url_comments = url_base

	spec_name = ""
	while(flag):
		r = requests.get(url_comments)
		soup = BeautifulSoup(r.text, "lxml")
		
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
				print "date is: ", record["date"]
				content = ""
	   			for comment_item in comment_div:
	   				content += u"【" + comment_item.div.text[:-1] + u"】"
					content += comment_item.select("div.pingyu")[0].text.strip()
					content += "\n"
				print content						
				
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

		page_all = soup.body.find_all("div", class_="xgo_cars_page")
		if (page_all != [] and page_all[0].find_all("a", class_="next") != []):
			page_num += 1
			url_comments = url_base[:-6] + str(page_num) + ".html"
			print "another_page, ", url_comments
		else:
			flag = 0
		# cur.commit()
	file.close()
	log.close()
	# print html

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
	
		# Find comments from a specific user.
		for item in soup.body.select("ul.pllist > li"):
			try:
				#print item
				spec_name = series + "".join(item.select("div.pltit")[0].h3.a.text.split())
				#print item.select("span.time")[0].text
				date = item.select("span.time")[0].text.split(u"发表于")[-1].strip()
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
				print content
	   			store_comment(web_name, record, content.strip(), file)
	   			
			except Exception as e:
				print e
				print url_comments
              			log.write("Error when crawling page: " + url_comments + "\n\n")

		next_page = soup.body.select("div.pagelist_new li.bg_white")[0].previous_sibling.previous_sibling
		if next_page.attrs == {}: # no class named "unable"
			page_num += 1
			url_comments = url_base.split("dianping")[0] + "dianping_1_" + str(page_num) + ".html"
			print "another_page, ", url_comments
		else:
			flag = 0

	file.close()
	log.close()
	# print html

def netease_crawler(brand, series, url_base):
	log = open("crawler_log.txt", "a")
	file_name = str(series) + ".txt"
	file = open(file_name, "a")

	web_name = u"网易汽车网"
	spec_name = ""
	flag = 1
	page_num = 1
	url_comments = url_base
	last_comment = ""

	while(flag):
		r = requests.get(url_comments)
		soup = BeautifulSoup(r.text, "lxml")
		print url_comments
		
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
				content = ""
	   			comment_div = item.select("div.comBody")[0]
				record["url"] =  "http://product.auto.163.com" + comment_div.a["href"]
				print "url is: ", record["url"]

   				r = requests.get(record["url"])
   				soup = BeautifulSoup(r.text, "lxml")
   				content = soup.select("div.d3").text[0].strip()
	   			print "comment is: ", content

	   			record["respond"] = respond = item.select("li.reply")[0].text[3:-1]
	   			record["upvote"] = upvote = item.select("li.useful")[0].text[3:-1]
	   			record["downvote"] = downvote = item.select("li.unuseful")[0].text[3:-1]
	   			print "respond is %s" % respond
	   			print "upvote is %s" % upvote
	   			print "downvote is %s" % downvote

	   			if last_comment != content.strip():
	   				last_comment = content.strip()
	   				store_comment(web_name, record, content.strip(), file)
	   			
			# except Exception as e:
			# 	print url_comments
   #              print e
   #              log.write("Error when crawling page: " + url_comments + "\n\n")
		next_page = soup.body.select("div.commentList-main div.comment-pages .active")[0].next_sibling.next_sibling
		if next_page.get("class") == None:
			page_num += 1
			url_comments = url_base.split("/1_")[0] + "/" + str(page_num) + "_1.html"
			print "another_page, ", url_comments
		else:
			flag = 0

	file.close()
	log.close()
	# print html

def main():
	series = u"宝马3系"
	brand = u"宝马"
	if not os.path.exists("data/"):
		os.makedirs("data/")
	os.chdir("data/")

	# get all car lists & crawl basic!
	# url_series = "http://car.autohome.com.cn/config/series/66.html"
	# r = requests.get(url_series)
	# car_list_str = r.text.split("specIDs =")[1].split(";")[0]
	# car_list = [int(s.strip()) for s in car_list_str[1:-1].split(",")]
	# for car_id in car_list:		
	# 	url_basic = "http://car.autohome.com.cn/config/spec/" + str(car_id) + ".html"
	# 	car_name = crawl_basic(url_basic, car_id)

	# sort the url by last_visit.

	for url_comment in url_pool:
		eval(url_comment.url+"_crawler")(brand, series, url_comment)

	# url_comment = "http://k.autohome.com.cn/66/ge0/0-0-2"
	# autohome_crawler(brand, series, url_comment)

	# url_comment = "http://car.bitauto.com/baoma3xi/koubei/tags/%E7%BB%BC%E5%90%88/"
	# yiche_crawler(brand, series, url_comment)

	# url_comment = "http://price.pcauto.com.cn/comment/sg424/t1/p1.html"
	# pcauto_crawler(brand, series, url_comment)

	# # xgo has no detailed classification.
	# url_comment = "http://www.xgo.com.cn/2710/list_s1_p1.html"
	# xgo_crawler(brand, series, url_comment)

	# url_comment = "http://db.auto.sohu.com/huachenbmw/1232/dianping_1.html"
	# sohu_crawler(brand, series, url_comment)

	# url_comment = "http://product.auto.163.com/opinion_more/1990/1_1.html"
	# netease_crawler(brand, series, url_comment)


	#cur.close()
	#conn.close()

main()

