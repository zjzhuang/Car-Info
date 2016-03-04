import urllib,urllib2,cookielib
import requests
from bs4 import BeautifulSoup
import sys, os
import json


reload(sys)  
sys.setdefaultencoding('utf8')   

def crawl_comment(url_base, dir, spec_name):
	
	files = os.listdir(dir)
	file_name = spec_name + ".txt"
	for name in files:
		if name.find(spec_name) != -1:
			file_name = name
			break
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
			
		for item in soup.body.find_all("div", id="topiclistshow")[0].find_all("dl"):
			url_comment_list = item.find_all("ul", class_="cont_list")[0].find_all("li")
			for url_comment in url_comment_list:
				r = requests.get(url_comment.a.get("href"))
				soup = BeautifulSoup(r.text, "lxml")
				comment = soup.find("div", id="content_bit").find_all("div", class_="article-contents")[0]	
				if comment.select("p.czjg_xq_cont") != []: # which means that comment is not valid.
					continue
				# print comment.text
				file.write("%%" + comment.text.strip() + "\n")
	file.close()
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
