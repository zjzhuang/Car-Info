#!/usr/bin/env python
# -*- coding: utf8 -*-

import urllib,urllib2,cookielib
import requests
from bs4 import BeautifulSoup
import sys, os, time
import json
import copy, collections, datetime, MySQLdb

reload(sys) 
sys.setdefaultencoding('utf8')   

comment_field = ["brand", "series", "spec", "dateNtime", "web", "url", "space", "power", "operation", "oilwear", "comfort", "appearance", "decoration", "costperformance", "upvote", "downvote", "respond"]
split_tag = ["【最满意的一点】", "【最不满意的一点】", "【空间】","【动力】","【操控】","【油耗】","【舒适性】","【外观】","【内饰】","【性价比】","【故障】","【保养】","【其他描述】"]

tran_tag={'【最满意的一点】':'advantage','【最不满意的一点】':'shortcoming', '【空间】':'space','【动力】': 'power', '【操控】':'operation', '【油耗】':'oilwear', '【舒适性】':'comfort', '【外观】':'appearance','【内饰】' :'decoration', '【性价比】':'costperformance','【故障】': 'failure', '【保养】':'maintenance','【其他描述】': 'other'}

tag = ["space", "power", "operation", "oilwear", "comfort", "appearance", "decoration", "costperformance"]

comment_dict = collections.OrderedDict()    
for field in comment_field:
    comment_dict[field] = ""

url_pool = [
    # {"web":"autohome", "firm":u"奔驰", "brand":u"北京奔驰", "series":u"奔驰GLC", "url":"http://k.autohome.com.cn/66/", "last_visit":time.clock(), "last_content":""}
]

def get_car_series():
    global url_pool

    #autohome begin
    web = "autohome"
    url_basic = "http://www.autohome.com.cn/grade/carhtml/"
    cnt = 0
    for i in range(ord("A"), ord("Z")+1):
        url_series = url_basic + chr(i) + ".html"
        r = requests.get(url_series)
        soup = BeautifulSoup(r.text, "lxml")
        for item in soup.find_all("dl"):
            firm = item.dt.div.text
            for brand_item in item.select("div.h3-tit"):
                brand = brand_item.text
                for li in brand_item.next_sibling.next_sibling.select("li"):
                    if li.select("span.text-through") != []:
                        continue
                    if li.select("a") == []:
                        continue
                    series = li.h4.text
                    url = li.select("div")[-1].select("a")[-1]["href"].split("#")[0] + "ge0/0-0-2"
                    print "series: ", series, "url: ", url
                    cnt += 1
                    url_pool.append({"web":web, "firm":firm, "brand":brand, "series":series, "url":url, "last_visit":time.clock(), "last_content":""})
    print "###########"
    print "autohome cnt: ", cnt
    print "###########"
    # #yiche begin
    # web = "yiche"
    # cnt = 0
    # url_basic = "http://api.car.bitauto.com/CarInfo/MasterBrandToSerialNew.aspx?type=2&pid=0&rt=master&serias=m&key=master"
    # r = requests.get(url_basic)
    # brand_list = json.loads(r.text.split('["master"]=')[-1])
    # for item in brand_list.values():
    #   firm = item["name"]
    #   url_series = "http://api.car.bitauto.com/CarInfo/MasterBrandToSerialNew.aspx?type=2&pid=%d&rt=serial&serias=m&key=serial&include=1" % int(item["id"])
    #   r = requests.get(url_series)
    #   series_list = json.loads(r.text.split('["serial"]=')[-1])
    #   for series_item in series_list.values():
    #       brand = series_item["goname"]
    #       series = series_item["showName"]
    #       url = "http://car.bitauto.com/%s/koubei/tags/综合/" % series_item["urlSpell"]
    #       print "series: ", series, "url: ", url
    #       url_pool.append({"web":web, "firm":firm, "brand":brand, "series":series, "url":url, "last_visit":time.clock(), "last_content":""})
    #       cnt += 1
            
    # print "###########"
    # print "yiche cnt: ", cnt
    # print "###########"
    # #pcauto begin
    # web = "pcauto"
    # cnt = 0
    # url_basic = "http://www.pcauto.com.cn/"
    # r = requests.get(url_basic)
    # soup = BeautifulSoup(r.text, "lxml")
    # for brand_item in soup.select("#brand_3 option")[1:]:
    #   firm = brand_item.text.strip()[2:]
    #   url_series = "http://price.pcauto.com.cn/interface/5_3/serial_json_chooser.jsp?brand=%d&callback=callback" % int(brand_item.attrs["value"])
    #   r = requests.get(url_series)
    #   series_list = json.loads(r.text.split("callback(")[-1][:-2]).values()[0]
    #   for series_item in series_list:
    #       if series_item["id"][0] == "+":
    #           brand = series_item["text"]
    #           continue
    #       series = series_item["text"]
    #       url = "http://price.pcauto.com.cn/comment/sg%d/t1/p1.html" % int(series_item["id"])
    #       print "series: ", series, "url: ", url
    #       url_pool.append({"web":web, "firm":firm, "brand":brand, "series":series, "url":url, "last_visit":time.clock(), "last_content":""})
    #       cnt += 1
            
    # print "###########"
    # print "pcauto cnt: ", cnt
    # print "###########"
    #xgo begin
    # web = "xgo"
    # cnt = 0
    # url_basic = "http://www.xgo.com.cn/brand.html"
    # r = requests.get(url_basic)
    # soup = BeautifulSoup(r.text, "lxml")
    # for firm_item in soup.select("div.main_nr"):
    #   firm = firm_item.select("div.l a")[-1].text
    #   for brand_item in firm_item.select("div.r div.car"):
    #       brand = brand_item.text or firm
    #       for series_item in brand_item.next_sibling.select("li"):
    #           series = series_item.dl.dt.text
    #           url = series_item.dl.dt.a["href"] + "list_s1_p1.html"
    #           print "series: ", series, "url: ", url
    #           url_pool.append({"web":web, "firm":firm, "brand":brand, "series":series, "url":url, "last_visit":time.clock(), "last_content":""})
    #           cnt += 1
            
    # print "###########"
    # print "xgo cnt: ", cnt
    # print "###########"
    # #sohu begin
    # web = "sohu"
    # cnt = 0
    # url_basic = "http://db.auto.sohu.com/index.shtml"
    # r = requests.get(url_basic)
    # soup = BeautifulSoup(r.text, "lxml")
    # for firm_item in soup.select("div.category_main"):
    #   firm = firm_item.select("p.car_brand")[0].text
    #   for brand_item in firm_item.select("div.meta_con"):
    #       brand = brand_item.div.a.text
    #       for series_item in brand_item.select("ul li"):
    #           series = series_item.select("a.name")[0].text
    #           # if no comments on this serial.
    #           if series_item.select("a.del") != []:
    #               continue
    #           url = series_item.select("dd")[1].select("a")[1]["href"][:-5] + "_1.html"
    #           print "series: ", series, "url: ", url
    #           url_pool.append({"web":web, "firm":firm, "brand":brand, "series":series, "url":url, "last_visit":time.clock(), "last_content":""})
    #           cnt += 1
            
    # print "###########"
    # print "sohu cnt: ", cnt
    # print "###########"
    # #netease begin
    # # web = "netease"
    # # url_basic = 

    return url_pool


def store_comment(web_name, record):
    # processing raw_comment
    # store it in sql.
    T=[]
    i=0
    for (key, value) in record.items():
        T.append(value)
        
    try:
        conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='1234',db='car',port=3306)
        cur=conn.cursor()

        conn.set_character_set('utf8')

        cur.execute('SET NAMES utf8;')
        cur.execute('SET CHARACTER SET utf8;')
        cur.execute('SET character_set_connection=utf8;')

        sql='insert into score values(%s, %s , %s , %s ,%s , %s , %s , %s ,%s , %s , %s , %s ,%s , %s , %s , %s , %s);'
        cur.execute(sql, T)
        
        cur.close()
        conn.commit()
        conn.close()
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    return


def autohome_crawler(brand, series, url_base, last_visit, last_content):
    web_name = "autohome"
    cur_content = ""

    flag = 1
    # is_new = 1
    cnt = 0
    page_num = 1
    url_comment = url_base
    while(flag):
        r = requests.get(url_comment)
        soup = BeautifulSoup(r.text)
        for item in soup.body.find_all("div", class_="mouthcon"):
            # try:
            record = copy.copy(comment_dict)
            record["brand"] = brand
            record["series"] = series
            record["spec"] = "".join(item.select("div.mouthcon-cont-left dl.choose-dl dd")[0].text.split())
            record["web"] = web_name
            record["url"] = item.select(".mouth-main .mouth-item .cont-title .title-name a")[0]["href"]
        
            # write additional info         
            record["upvote"] = upvote = item.select(".mouth-main .mouth-remak label.supportNumber")[0].text
            record["respond"] = respond = item.select(".mouth-main .mouth-remak span.CommentNumber")[0].text
            print "upvote is " + upvote
            print "respond is " + respond
            comment_date = item.select(".mouth-main .mouth-item .title-name b")[-1].text.strip()
            print "date: ", comment_date

            scores = item.select(".score-small")
            for i in range(len(scores)):
            	record[tag[i]] = scores[i].next_sibling.text

            record["dateNtime"] = comment_date
            cnt += 1
            store_comment(web_name, record)
            
            # except Exception as e:
            #   print e
        
        page_next = soup.body.find_all("a", class_="page-item-next")
        # Get next page.
        if (page_next != [] and page_next[0].get("href") != "###"):
            page_num += 1
            url_comment = url_base + "/index_" + str(page_num) + ".html"
        else:
            flag = 0
    if cnt == 0:
        print "No comment in url: ", url_base


def main():
    global url_pool

    if not os.path.exists("data/"):
        os.makedirs("data/")
    os.chdir("data/")

    # get all series!
    if not os.path.exists("url_pool.txt"):
        url_pool = get_car_series()
        with open("url_pool.txt", "w") as f:
            json.dump(url_pool, f)
        f.close()
    else:
        f = open("url_pool.txt", "r")
        url_pool = json.load(f)

    # sort the url by last_visit.
    for url_comment in url_pool:
		if url_comment["web"] == "autohome":
		    eval(url_comment["web"]+"_crawler")(url_comment["brand"], url_comment["series"], url_comment["url"], url_comment["last_visit"], url_comment["last_content"])

main()