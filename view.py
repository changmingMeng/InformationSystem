#! /usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import tornado.ioloop
import tornado.web
import tornado.escape
import json
import time
import datetime

from models import *
import control
import baiduMap
from utils import Utils
import excel2DB


dataroots = [r'F:\36服务器搬迁资料\02-外部共享\21-2014年GSM日常作业计划\话务量&流量指标月备份',
             r'F:\36服务器搬迁资料\02-外部共享\23-2014年WCDMA日常作业计划\话务量&流量指标月备份',
             r'F:\36服务器搬迁资料\02-外部共享\22-2014年LTE日常作业计划\爱立信\LTE小区级日数据流量及忙时KPI指标备份',
             r'F:\36服务器搬迁资料\02-外部共享\22-2014年LTE日常作业计划\华为\LTE小区级日数据流量及忙时KPI指标备份']

# class MainHandler(tornado.web.RequestHandler):
#   """主索引的处理"""
#   def get(self):
#       print "running MainHandler get()"
#       self.redirect('/login', permanent=False, status=302)



# class LoginHandler(tornado.web.RequestHandler):
#   """登录界面的请求处理"""
#   def get(self):
#       print "running LoginHandler get()"
#       self.render("login.html")
#
#   def post(self):
#     #debug版伪登入
#     print "running LoginHandler post()"
#     account = self.get_argument("account")
#     password = self.get_argument("password")
#     print account, password
#     if account == password:
#       self.redirect('/manage', permanent=False, status=302)
#     else:
#       self.add_header("userlogin", "fail")


class ManageHandler(tornado.web.RequestHandler):
  """处理管理界面的请求"""
  def get(self):
    print "running ManageHandler get()"
    self.render('result.html')



class SelectHandler(tornado.web.RequestHandler):
    """从数据库选择数据"""

    def get(self):
        print "select.get"

        selectname = self.get_argument('name')
        print selectname
        nettype = self.get_argument('type')
        print nettype
        date = self.get_argument('date')
        end_date = self.get_argument('end_date')
        print date

        likename = '%'+selectname+'%'
        print likename

        if date.replace(" ","") == "":
            sql = CellBusi3G.select()\
                .where(CellBusi3G.name % likename) \
                .order_by(CellBusi3G.name, CellBusi3G.date) \
                .limit(50)
        else:
            if end_date.replace(" ","") == "":
                sql = CellBusi3G.select()\
                    .where((CellBusi3G.name % likename)
                           & (CellBusi3G.date == Utils.strdate_to_date(date))) \
                    .order_by(CellBusi3G.name, CellBusi3G.date) \
                    .limit(50)
            else:
                sql = CellBusi3G.select() \
                    .where((CellBusi3G.name % likename)
                           & (CellBusi3G.date >= Utils.strdate_to_date(date))
                           & (CellBusi3G.date <= Utils.strdate_to_date(end_date))) \
                    .order_by(CellBusi3G.name, CellBusi3G.date) \
                    .limit(50)


        response = "["
        if sql is not None:
            #response += "{'state':%s},"%(0,)
            for t in sql:
                name, date, erl, updata, downdata, alldata \
                = \
                t.name.name, t.date, t.erl, t.updata, t.downdata, t.alldata
                response+="{'name':'%s','date':'%s','erl':%s, 'updata':%s, 'downdata':%s, 'alldata':%s}," % \
                     (name, date, round(erl, 3), round(updata/1024, 2), round(downdata/1024, 2), round(alldata/1024, 2))
        response+="]"
        print response
        response_json = tornado.escape.json_encode(response)
        self.write(response_json)

    def post(self):
        print "select.post"

        selectname = self.get_argument('name')
        print selectname
        nettype = self.get_argument('type')
        print nettype
        date = self.get_argument('date')
        print date
        t = CellBusi3G.select().where(CellBusi3G.name == selectname).first()
        if t is not None:
            name, date, erl, updata, downdata, alldata = t.name.name, t.date, t.erl, t.updata, t.downdata, t.alldata
            print name

            self.write("%s,%s,%s,%s,%s,%s,%s,"%(0, name, date, round(erl), round(updata/1024, 2), round(downdata/1024, 2), round(alldata/1024, 2)))

        else:
            #self.render("select.html", error='请输入正确的小区名称')
            self.write("1")


class ZoneHandler(tornado.web.RequestHandler):


    def get(self):
        print("ZoneHandler.get")
        self.render("zone.html")

class UploadHandler(tornado.web.RequestHandler):


    def prepare(self):
        self.filepath = ""

    def get(self):
        print("uploadhandler.get")
        if self.filepath == "":
            pass
        else:
            begindate = self.get_argument("begin_date")
            enddate = self.get_argument("end_date")

    def post(self):
        print("uploadhandler.post")

        begindate = self.get_argument("begin_date")
        enddate = self.get_argument("end_date")
        print begindate, enddate


        upload_path = os.path.join(os.path.dirname(__file__), 'files')  # 文件的暂存路径
        file_metas = self.request.files['file']  # 提取表单中‘name’为‘file’的文件元数据
        for meta in file_metas:
            filename = meta['filename']
            filename = str(time.time()).replace(".","") + filename
            filepath = os.path.join(upload_path, filename)
            self.filepath = filepath
            with open(filepath, 'wb') as up:  # 有些文件需要以二进制的形式存储，实际中可以更改
                up.write(meta['body'])
        print begindate, enddate, filepath

        sql = control.control.getZoneInfo(begindate, enddate, filepath)

        response = "["
        if sql is not None:
            # response += "{'state':%s},"%(0,)
            for t in sql:
                response += "{'erl':%s, 'updata':%s, 'downdata':%s, 'alldata':%s}," % \
                            (round(t.erl, 3), round(t.updata / 1024, 2), round(t.downdata / 1024, 2),
                             round(t.alldata / 1024, 2))
        response += "]"
        print response
        response_json = tornado.escape.json_encode(response)
        self.write(response_json)


class DownloadHandler(tornado.web.RequestHandler):
    def get(self):
        #filename = "zero_cell.xlsx"
        filename = self.get_argument("filename")
        #self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Type', 'application/x-download')
        self.set_header('Content-Disposition', 'attachment; filename=' + filename)
        buf_size = 4096
        download_path = os.path.join(os.path.dirname(__file__), 'downFiles')
        filepath = os.path.join(download_path, filename)
        with open(os.path.join('', filepath), 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                self.write(data)
        self.finish()

# class MapHandler(tornado.web.RequestHandler):
#
#     def get(self):
#         self.render("map3.html")
#
#
# class SearchHandler(tornado.web.RequestHandler):
#     def get(self):
#         addresslist = baiduMap.readCSV(r"F:\视频组\地址经纬度\7033003223217169.csv".decode("utf-8").encode("GBK"))
#         #response_json = tornado.escape.json_encode(addresslist)
#         response_json = json.dumps(addresslist)
#         self.write(response_json)

class ZeroBusiHandler(tornado.web.RequestHandler):

    def get(self):
        print "ZeroBusiHandler.get"
        self.render("zero.html")

    def post(self):
        print "ZeroBusiHandler.post"
        begindate = self.get_argument("begin_date")
        enddate = self.get_argument("end_date")
        nettype = self.get_argument("net_type")
        days = self.get_argument("days")
        threshold = self.get_argument("threshold")
        busitype = self.get_argument("busitype")
        print begindate, enddate, nettype, days, threshold, busitype

        result = control.control.getNobusiCell(int(days), float(threshold), nettype, busitype)
        #在服务器本地生成文件
        download_path = os.path.join(os.path.dirname(__file__), 'downFiles')
        filename = str(time.time()).replace(".","")+'zero_cell.xlsx'
        control.control.write2Excel(result, os.path.join(download_path, filename))
        filejson = "'" + filename + "'"
        #以json形式返回到浏览器
        data = "["
        if result is not None:
            # response += "{'state':%s},"%(0,)
            for t in result:
                data += "{'name':'%s', 'date':'%s', 'nettype':'%s'}," % \
                            (t[0], t[1], nettype)
        data += "]"
        print data
        response = "["+filejson+","+data+"]"
        response_json = tornado.escape.json_encode(response)
        self.write(response_json)


class BackstageHandler(tornado.web.RequestHandler):

    def get(self):
        user = self.get_argument('user')
        code = self.get_argument('code')
        date = self.get_argument('date')
        operation = self.get_argument('operation')
        if user == 'UnicomWangyou':
            if code == 'Year' and operation == 'Insert':
                for dataroot in dataroots:
                    excel2DB.multi_import(dataroot.decode('utf-8').encode('GBK'), date)


#http://10.117.240.36:8000/back?user=UnicomWangyou&code=Year&date=2017&operation=Insert



def make_app():
    return tornado.web.Application([(r'/', ManageHandler),
                                    #(r'/login', LoginHandler),
                                    (r'/manage', ManageHandler),
                                    (r'/select', SelectHandler),
                                    (r'/zone', ZoneHandler),
                                    (r'/zero', ZeroBusiHandler),
                                    (r'/upload', UploadHandler),
                                    (r'/download', DownloadHandler),
                                    (r'/back', BackstageHandler),
                                    #(r'/map', MapHandler),
                                    #(r'/search', SearchHandler)
                                    ],
      cookie_secret='jf0239u0fr9n',
      template_path=os.path.join(os.path.dirname(__file__), "templates"),
      static_path=os.path.join(os.path.dirname(__file__), "static"),
      debug=True,
    )

def read_data_to_db():
    print datetime.datetime.now(), "read_data_to_db"

    date = datetime.datetime.now().date()
    for dataroot in dataroots:
        excel2DB.multi_import_by_date(dataroot.decode('utf-8').encode('GBK'), date)


def general_zero_temp_table():
    print datetime.datetime.now(), "read_data_to_db"

def check_cell_busi():
    print datetime.datetime.now(), "read_data_to_db"

def scheduled_tasks():
    now_time = time.localtime(time.time()).tm_hour
    if now_time == 6:
        general_zero_temp_table()
    elif now_time == 7:
        check_cell_busi()
    elif now_time == 23:
        read_data_to_db()


if __name__ == "__main__":
  app = make_app()
  app.listen(8000)
  tornado.ioloop.PeriodicCallback(scheduled_tasks, 60*60*1000).start()
  tornado.ioloop.IOLoop.current().start()
