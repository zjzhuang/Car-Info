import urllib,urllib2,cookielib
import requests
from bs4 import BeautifulSoup
import sys, os
import json


reload(sys)  
sys.setdefaultencoding('utf8')   

def crawl_comment(web_name, series, url_base, spec_name = "null"):

	# open the log.
	log = open("crawler_log.txt", "a")
	
	# get the file name.
	file_name = "data/" + str(series) + ".txt"

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
			try:
	   			comment_div = item.select("dd.paragraph > div.clearfix")

	   			comment = "from: %s\nspec: %s\ndate: %s\ncontent: " % (web_name, spec_name, item.select("dd.title span.r")[0].text[4:]) 

	   			for comment_item in comment_div:
	   				comment += comment_item.text
					print comment_item.text
			
	   			comment += "\nrespond: %s\nupvote: %s\ndownvote: %s\n\n" % tuple(i.text for i in item.select("div.apply span.redc00"))
				
	   			file.write(comment)
			except Exception as e:
				print url_comments
		                print e
                		log.write("Error when crawling page: " + url_comments + "\n\n")

	file.close()
	log.close()
	# print html

def main():
	# just a temperary name. Will change later.
	series = 66
	dir = os.getcwd() + "/data/" + str(series) + "/"
	if not os.path.exists("data/" + str(series)):
		os.makedirs("data/" + str(series))
	# os.chdir("data/"+str(series))

	# xgo has no detailed classification.
	url_comment = "http://www.xgo.com.cn/2710/list_s1_p1.html"
	
	crawl_comment(u"xgo", series, url_comment)

main()
