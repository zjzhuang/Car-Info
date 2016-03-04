
import urllib,urllib2,cookielib
import requests
from bs4 import BeautifulSoup
import sys, os
import json


reload(sys)  
sys.setdefaultencoding('utf8')   


def get_car_id(url_series):
	r = requests.get(url_series)
	car_list_str = r.text.split("specIDs =")[1].split(";")[0]
	car_list = [int(s.strip()) for s in car_list_str[1:-1].split(",")]
	return car_list

def crawl_basic(url_basic):
	r = requests.get(url_basic)
	
	configList = r.text.split("config = ")[1].split(";")[0]
	configList = json.loads(configList)
	car_name = configList["result"]["paramtypeitems"][0]["paramitems"][0]["valueitems"][0]["value"]
	print type(car_name)
	file_name = car_name.encode("utf8") + car_name.encode("gbk") + "_basic" + ".txt"
	file = open(file_name, 'w')

	# extract basic infomation.
	basic_config = {}

	for item in configList["result"]["paramtypeitems"][0]["paramitems"]:
		basic_config[item["name"]] = item["valueitems"][0]["value"]
		# print item["name"], basic_config[item["name"]]
		# should encode it using the charset. Ref: http://www.tuicool.com/articles/rUNZ7b
		file.write("%%" + item["name"] + ":" + basic_config[item["name"]] + "\n") 

	file.close()
	return car_name

def crawl_comment(url_base, car_name):
	file_name = car_name.encode("utf8") + "_comment" + ".txt"
	file = open(file_name, "w")
	flag = 1
	url_comment = url_base
	page_num = 1
	while(flag):
		r = requests.get(url_comment)
		soup = BeautifulSoup(r.text, "lxml")
		page_next = soup.body.find_all("a", class_="page-item-next")
		if (page_next != [] and page_next[0].get("href") != "###"):
			page_num += 1
			url_comment = url_base + "/index_" + str(page_num) + ".html"
			# print url_comment
		else:
			flag = 0
			
		for item in soup.body.find_all("div", class_="mouthcon"):
			file.write("%%" + item.select(".mouth-main .text-con div")[0].text + "\n##")
			file.write(item.select(".mouth-main .mouth-remak label.supportNumber")[0].text + "\n\n\n")
	file.close()
	# print html

def main():

	series = 66
	if not os.path.exists("data/" + str(series)):
		os.makedirs("data/" + str(series))
	os.chdir("data/"+str(series))
	url_series = "http://car.autohome.com.cn/config/series/" + str(series) + ".html"
	car_list = get_car_id(url_series)
	
	for car_id in car_list:		
		print "Processing", car_id, "..."
		url_basic = "http://car.autohome.com.cn/config/spec/" + str(car_id) + ".html"
		url_comment = "http://k.autohome.com.cn/spec/" + str(car_id)
		car_name = crawl_basic(url_basic)
		crawl_comment(url_comment, car_name)

main()

