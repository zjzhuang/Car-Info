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
		if name.find(spec_name) != -1 and name.find("basic") == -1:
			file_name = name
			break
		if spec_name.find(name) != -1:
			os.rename(dir + name, dir + file_name)
			break
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
			comment = item.select("div.table_text")[0]
			print "text:", comment.text.strip()
			file.write("%%" + comment.text + "\n")
			for add_on in item.select("div.zjdp"):
				file.write("@@" + add_on.select("div.zjdp_text").text  + "\n")
			file.write("\n\n\n")
	file.close()
	# print html

def main():
	# just a temperary name. Will change later.
	series = 66
	dir = os.getcwd() + "/data/" + str(series) + "/"
	if not os.path.exists("data/" + str(series)):
		os.makedirs("data/" + str(series))
	os.chdir("data/" + str(series))
	# to crawl a car series.
	url_series = "http://price.pcauto.com.cn/comment/sg424/"
	
	r = requests.get(url_series)

	soup = BeautifulSoup(r.text, "lxml")
	
	# Note that it only crawls those specs which are currently sold.
	for item in soup.select("#cxList div.tr"):		
		# find a certain spec
		url_comment = item.find("a").get("href")
		spec_name = "".join(item.find("a").text.strip().split())
		crawl_comment(url_comment, dir, spec_name)

	# crawl those unavaliable specs.
	r = requests.get(url_series + "/sale/")
	soup = BeautifulSoup(r.text, "lxml")
        for item in soup.select("#cxList div.tr")[0].ul.children:               
                # find a certain spec
                url_comment = item.find("a")["href"]
                spec_name = "".join(item.find("a").text.strip().split())
                crawl_comment(url_comment, dir, spec_name)


main()
