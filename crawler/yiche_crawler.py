import urllib,urllib2,cookielib
import requests
from bs4 import BeautifulSoup
import sys, os
import json


reload(sys)  
sys.setdefaultencoding('utf8')   

def crawl_comment(url_base, dir, spec_name):

	# open the log.
	log = open("crawler_log.txt", "a")
	
	# get the file name.
	files = os.listdir(dir)
	file_name = spec_name + ".txt"

	has_file = 0
	for name in files:
		if name.find(spec_name) != -1 and name.find("basic") == -1:
			file_name = name
			has_file = 1
			break
	if has_file == 0:
		print "No data matched."
		return 
	file = open(file_name, "a")
	file.write("**comments from yiche\n\n\n")
	flag = 1
	url_comments = url_base
	page_num = 1



	while(flag):
		r = requests.get(url_comments)
		soup = BeautifulSoup(r.text, "lxml")
		page_all = soup.body.find_all("span", id_="main_pager_down")
		if (page_all != [] and page_all[0].find_all("a", class_="next_on") != []):
			page_num += 1
			url_comments = url_base + "page" + str(page_num)
			print "another_page, ", page_num
		else:
			flag = 0
		
		# Find comments from a specific user.
		for item in soup.body.find_all("div", id="topiclistshow")[0].find_all("dl"):
			try:
				url_comment_list = item.find_all("ul", class_="cont_list")[0].find_all("li")
			except e:
                                print e
                                log.write("Error when crawling page: " + url_comments + "\n Error msg: " + e + "\n\n")

			# One user may have several comments.
			for url_comment in url_comment_list:
				r = requests.get(url_comment.a.get("href"))
				soup = BeautifulSoup(r.text, "lxml")
				try:
					comment = soup.find("div", id="content_bit").find_all("div", class_="article-contents")[0]
						
					if comment.select("p.czjg_xq_cont") != []: # which means that comment is not valid.
						continue
					# pre-process the text for convenience.
					for tag in comment.find_all("strong"):
						if not tag.string:
							continue
						tag.string = "[" + tag.string.strip() + "]"
						# print tag.text
					for p in comment.find_all("p"):
						if not p.string:
							continue
						p.string = p.string.strip()
					if comment.h4:
						comment.h4.extract()
					if comment.pre:
						comment.pre.extract()
					if comment.find("div.con_nav2"):
						comment.find("duv.con_nav2").extract()
					file.write("%%" + comment.text.strip() + "\n")
				except Exception as e:
					print url_comment.a.get("href")
                                        print e
                                        log.write("Error when crawling page: " + url_comment.a.get("href") + "\n\n")

	file.close()
	log.close()
	# print html

def main():
	# just a temperary name. Will change later.
	series = 66
	dir = os.getcwd() + "/data/" + str(series) + "/"
	if not os.path.exists("data/" + str(series)):
		os.makedirs("data/" + str(series))
	os.chdir("data/"+str(series))
	# a car series
	url_series = "http://car.bitauto.com/baoma3xi/koubei/tags/%E7%BB%BC%E5%90%88/"
	
	r = requests.get(url_series)

	soup = BeautifulSoup(r.text, "lxml")

	is_first = 1
	for item in soup.body.findAll("div", id="trimlist")[0].ul.children:		
		if item.find("a") == -1:
			continue
		if is_first == 1:
			is_first = 0
			continue
		# find a certain spec
		url_comment = item.find("a")["href"]
		spec_name = "".join(item.find("a").text.strip().split())
		print "processing ..."
		crawl_comment(url_comment, dir, spec_name)

main()
