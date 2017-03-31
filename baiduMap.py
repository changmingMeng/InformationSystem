#! /usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import csv
import json
import urllib2
import  httplib
import chardet

url = 'http://api.map.baidu.com/geocoder/v2/'
ak = '&ak=Rl3cuYvuDMBES9TULIixBWAIOi0ES7BN'  # 百度地图api密钥
# back='&callback=renderReverse&location='
address = 'address='
location = '华景新城'
city = '&city=广州'

citylimit = '&city_limit=true'
output = '&output=json'

url = url + '?' + address + location + city + output + ak
print url

temp = urllib2.urlopen(url)
# console.log(data)
print temp, "strtype:", chardet.detect(temp.read())
print temp.read()
#str = '{"status":0,"result":{"location":{"lng":113.36936290434473,"lat":23.139391660850447},"precise":0,"confidence":50,"level":"地产小区"}}'
#str_json = json.loads(str)
#print "str_json:", str_json
#print "lin", str_json["result"]["location"]["lng"]

new_str = temp.read()
hjson = json.loads(new_str)
location = hjson["result"]["formatted_address"]  # 省，市，县
print location
info = hjson["result"]["sematic_description"]  # 详细描述
print info
