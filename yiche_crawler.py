import urllib,urllib2,cookielib
import requests
from bs4 import BeautifulSoup
import sys, os
import json


reload(sys)  
sys.setdefaultencoding('utf8')   

def crawl_comment(url_base):
	
	file_name = "yiche_comment_" + url_base.split("/")[-2] + ".txt"
	print file_name
	file = open(file_name, "w")
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
			url_comment = item.find_all("ul", class_="cont_list")[0].li.a.get("href")
			r = requests.get(url_comment)
			soup = BeautifulSoup(r.text, "lxml")
			# TODO: Some comments are not totally cleaned up. Other contents besides the real one are included.
			print soup.find("div", id="content_bit").find_all("div", class_="article-contents")[0].text	
			#file.write("%%" + item.select(".mouth-main .text-con div")[0].text + "\n##")
			#file.write(item.select(".mouth-main .mouth-remak label.supportNumber")[0].text + "\n\n\n")
	file.close()
	# print html

def main():
	series = "test"
	if not os.path.exists("yiche_crawler/" + str(series)):
		os.makedirs("yiche_crawler/" + str(series))
	os.chdir("yiche_crawler/"+str(series))
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
		crawl_comment(url_comment)

main()
