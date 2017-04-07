#! /usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import tornado.ioloop
import tornado.web
import tornado.escape
import json

from models import *
import control
import baiduMap


class MainHandler(tornado.web.RequestHandler):
  """主索引的处理"""
  def get(self):
      print "running MainHandler get()"
      self.redirect('/login', permanent=False, status=302)



class LoginHandler(tornado.web.RequestHandler):
  """登录界面的请求处理"""
  def get(self):
      print "running LoginHandler get()"
      self.render("login.html")

  def post(self):
    #debug版伪登入
    print "running LoginHandler post()"
    account = self.get_argument("account")
    password = self.get_argument("password")
    print account, password
    if account == password:
      self.redirect('/manage', permanent=False, status=302)
    else:
      self.add_header("userlogin", "fail")


class ManageHandler(tornado.web.RequestHandler):
  """处理管理界面的请求"""
  def get(self):
    print "running ManageHandler get()"
    self.render('result.html')

class InsertHandler(tornado.web.RequestHandler):
  """向数据库存储信息"""
  def get(self):
    self.render("test.html")

  def post(self):
    province = self.get_argument('province')
    city = self.get_argument('city')
    carnum = self.get_argument('carnum')
    descript = self.get_argument('descript')
    print "view::InsertHandler", province, city, carnum, descript
    ctl = Control.Control()
    ctl.insert(province+city+carnum, descript, "E:/picture/")
    self.redirect('/manage')



class SelectHandler(tornado.web.RequestHandler):
    """从数据库选择数据"""

    def get(self):
        print "select.get"

        selectname = self.get_argument('name')
        print selectname
        nettype = self.get_argument('type')
        print nettype
        date = self.get_argument('date')
        print date

        likename = '%'+selectname+'%'
        print likename
        sql = CellBusi3G.select().where(CellBusi3G.name % likename).limit(50)

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
            filepath = os.path.join(upload_path, filename)
            self.filepath = filepath
            with open(filepath, 'wb') as up:  # 有些文件需要已二进制的形式存储，实际中可以更改
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

class MapHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("map3.html")


class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        addresslist = baiduMap.readCSV(r"F:\视频组\地址经纬度\7033003223217169.csv".decode("utf-8").encode("GBK"))
        #response_json = tornado.escape.json_encode(addresslist)
        response_json = json.dumps(addresslist)
        self.write(response_json)





def make_app():
    return tornado.web.Application([(r'/', ManageHandler),
                                    (r'/login', LoginHandler),
                                    (r'/manage', ManageHandler),
                                    (r'/select', SelectHandler),
                                    (r'/zone', ZoneHandler),
                                    (r'/upload', UploadHandler),
                                    (r'/map', MapHandler),
                                    (r'/search', SearchHandler),
                                    (r'/insert',InsertHandler)],
      cookie_secret='jf0239u0fr9n',
      template_path=os.path.join(os.path.dirname(__file__), "templates"),
      static_path=os.path.join(os.path.dirname(__file__), "static"),
      debug=True,
    )


if __name__ == "__main__":
  app = make_app()
  app.listen(8000)
  tornado.ioloop.IOLoop.current().start()
