# encoding: utf-8

import xlrd
import psycopg2
import datetime

import utils
import dbManip
def timer(func):
    def warpper(*args, **kw):
        start = datetime.datetime.now()
        func(*args, **kw)
        end = datetime.datetime.now()
        print end-start
    return warpper

class Read3GFile(object):


    def __init__(self, filename):
        self.filename = filename
        # self.db = dbManip.dbManipulate()

    #@timer
    def read_excel(self):
        info_lst = []
        busi_lst = []

        with xlrd.open_workbook(self.filename) as workbook:
            sheet = workbook.sheet_by_index(0)
            print sheet.nrows
        for r in xrange(1,sheet.nrows):#excel第2行到最后一行
            row = sheet.row_values(r)

            #print row

            name = row[3]
            lac = int(row[1])
            ci = int(row[2])
            nodebname = row[4]
            rncname = row[5]
            fac = row[16]
            info_lst.append([name, lac, ci, nodebname, rncname, fac])

            date = self.exceldate_to_postgredate(row[0])
            erl = row[6]
            updata = row[8] + row[10]
            downdata = row[9] + row[11]
            sumdata = updata + downdata
            busi_lst.append([name, date, erl, updata, downdata, sumdata])

        return [info_lst, busi_lst]

    def connect_to_db(self):
        return psycopg2.connect(database="testdb",
                                  user="postgres",
                                  password="123456",
                                  host="127.0.0.1",
                                  port="5432")

    def save_info_firsttime(self, info_lst):
        dbconn = self.connect_to_db()
        dbcursor = dbconn.cursor()
        for info in info_lst:
            print info
            try:
                dbcursor.execute("insert into cell_info_3G (name, lac, ci, nodeb, rnc, fac)\
                                values(%s, %s, %s, %s, %s, %s)",info)
            except (psycopg2.IntegrityError, psycopg2.InternalError) as e:
                print e
        dbconn.commit()
        dbconn.close()

    @timer
    def save_info_not_firsttime(self, info_lst):
        dbconn = self.connect_to_db()
        dbcursor = dbconn.cursor()

        dbcursor.execute("create TEMPORARY table tmp_info_3g("
                         "name text NOT NULL,"
                         "lac text,"
                         "ci text,"
                         "nodeb text,"
                         "rnc text,"
                         "fac text,"
                         "PRIMARY KEY (name))")

        for info in info_lst:
            #print info
            try:
                dbcursor.execute("insert into tmp_info_3g (name, lac, ci, nodeb, rnc, fac)\
                                values(%s, %s, %s, %s, %s, %s)",info)
            except (psycopg2.IntegrityError, psycopg2.InternalError) as e:
                print e

        dbcursor.execute("select name from tmp_info_3g "
                         "except "
                         "select name from cell_info_3g")
        names = dbcursor.fetchall()
        names_new = [name[0] for name in names]

        print names
        print names_new

        for name in names_new:
            dbcursor.execute("insert into cell_info_3g "
                             "select * from tmp_info_3g "
                             "where name = '%s'"%name)

        dbconn.commit()
        dbconn.close()

    @timer
    def save_busi(self, busi_lst):
        dbconn = self.connect_to_db()
        dbcursor = dbconn.cursor()

        for busi in busi_lst:
            #print busi
            try:
                dbcursor.execute("insert into cell_busi_3g (name, date, erl, updata, downdata, alldata)\
                                values(%s, %s, %s, %s, %s, %s)",busi)
            except (psycopg2.IntegrityError, psycopg2.InternalError) as e:
                print e #如果出错则存储整个表的事务被回滚，进一步的处理有待研究
                        #
        dbconn.commit()
        dbconn.close()

    @staticmethod
    def exceldate_to_postgredate(date):
        return psycopg2.Date(*xlrd.xldate_as_tuple(date, 0)[:3])



def test():
    # rf = Read2GFile("E:\projects\excel2DB\data\G网监控常用指标-20170101.xlsx".decode("utf-8").encode("GBK"))
    rf = Read3GFile("E:\projects\excel2DB\data\W网监控常用指标-20170302.xlsx".decode("utf-8").encode("GBK"))
    info_lst, busi_lst = rf.read_excel()
    rf.save_info_not_firsttime(info_lst)
    rf.save_busi(busi_lst)

if __name__ == "__main__":
    test()
    # for i in xrange(2,5):
    #     print i
    #print datetime.datetime.now()