#! /usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import tornado.ioloop
import tornado.web
import tornado.escape

from models import *



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
                     (name, date, round(erl, 3), round(updata), round(downdata), round(alldata))
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
            # self.render("selectResult.html",
            #          name=name,
            #          date=date,
            #          updata=updata,
            #          downdata=downdata,
            #          alldata=alldata,
            #          erl=erl )
            self.write("%s,%s,%s,%s,%s,%s,%s,"%(0, name, date, round(erl), round(updata), round(downdata), round(alldata)))
            # self.render("sql.html",
            #          statue="0",
            #          name=name,
            #          date=date,
            #          updata=round(updata),
            #          downdata=round(downdata),
            #          alldata=round(alldata),
            #          erl=round(erl) )
        else:
            #self.render("select.html", error='请输入正确的小区名称')
            self.write("1")



class UploadHandler(tornado.web.RequestHandler):


    def post(self):
        upload_path = os.path.join(os.path.dirname(__file__), 'files')  # 文件的暂存路径
        file_metas = self.request.files['file']  # 提取表单中‘name’为‘file’的文件元数据
        for meta in file_metas:
            filename = meta['filename']
            filepath = os.path.join(upload_path, filename)
            with open(filepath, 'wb') as up:  # 有些文件需要已二进制的形式存储，实际中可以更改
                up.write(meta['body'])



def make_app():
    return tornado.web.Application([(r'/', ManageHandler),
                                    (r'/login', LoginHandler),
                                    (r'/manage', ManageHandler),
                                    (r'/select', SelectHandler),
                                    (r'/upload', UploadHandler),
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
