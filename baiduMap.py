#! /usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import csv
import json
import urllib2
import  httplib
import chardet

url = 'http://api.map.baidu.com/geocoder/v2/?address=华景新城&pois=1&city=广州&output=json'
ak = '&ak=Rl3cuYvuDMBES9TULIixBWAIOi0ES7BN'  # 百度地图api密钥
# back='&callback=renderReverse&location='
address = 'address='
location = '华景新城'
city = '&city=广州'

citylimit = '&city_limit=true'
output = '&output=json'

url = url + ak
print url

temp = urllib2.urlopen(url)
# console.log(data)
# print (temp, "strtype:", chardet.detect(temp.read()))
# print temp.read()
#str = '{"status":0,"result":{"location":{"lng":113.36936290434473,"lat":23.139391660850447},"precise":0,"confidence":50,"level":"地产小区"}}'
#str_json = json.loads(str)
#print "str_json:", str_json
#print "lin", str_json["result"]["location"]["lng"]

str = temp.read()
print str
file = open('e:\\test.txt','w')
file.write(str)
file.close()

file = open('e:\\test.txt', 'r')
str = file.read()
print str
data = json.loads(str)
lng = data["result"]["location"]["lng"]
lat = data["result"]["location"]["lat"]
print "lng=", lng, "lat=", lat
