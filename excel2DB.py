# encoding: utf-8

import xlrd
import psycopg2
import datetime
import chardet

from utils import Utils
import dbManip
def timer(func):
    def warpper(*args, **kw):
        start = datetime.datetime.now()
        func(*args, **kw)
        end = datetime.datetime.now()
        print end-start
    return warpper

class ReadExcelFile(object):


    def __init__(self, filename):
        self.filename = filename

    def connect_to_db(self):
        return psycopg2.connect(database="testdb",
                                  user="postgres",
                                  password="123456",
                                  host="127.0.0.1",
                                  port="5432")


class Read2GFile(ReadExcelFile):


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

            #date = self.exceldate_to_postgredate(row[0])
            date = Utils.exceldate_to_postgredate(row[0])
            erl = row[6]
            updata = row[8] + row[10]
            downdata = row[9] + row[11]
            sumdata = updata + downdata
            busi_lst.append([name, date, erl, updata, downdata, sumdata])

        return [info_lst, busi_lst]

class Read3GFile(ReadExcelFile):


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

            #date = self.exceldate_to_postgredate(row[0])
            date = Utils.exceldate_to_postgredate(row[0])
            erl = row[6]
            updata = row[8] + row[10]
            downdata = row[9] + row[11]
            sumdata = updata + downdata
            busi_lst.append([name, date, erl, updata, downdata, sumdata])

        return [info_lst, busi_lst]

    # def connect_to_db(self):
    #     return psycopg2.connect(database="testdb",
    #                               user="postgres",
    #                               password="123456",
    #                               host="127.0.0.1",
    #                               port="5432")

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

        #print names
        print len(names_new), " new cells"#, names_new

        for name in names_new:
            print name.decode("utf-8")
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

    def read_to_db(self):
        info_lst, busi_lst = self.read_excel()
        self.save_info_not_firsttime(info_lst)
        self.save_busi(busi_lst)


class Read4GFile(ReadExcelFile):


    def read_excel(self):
        info_lst = []
        busi_lst = []

        with xlrd.open_workbook(self.filename) as workbook:
            sheet = workbook.sheet_by_index(0)
            #print sheet.nrows
        for r in xrange(1,sheet.nrows):#excel第2行到最后一行
            row = sheet.row_values(r)

            #print row

            cell_name = row[2]
            base_name = row[1]
            base_id = int(row[3])
            cell_id = int(row[4])
            tac = int(row[5])
            pci = int(row[6])
            info_lst.append([cell_name, base_name, base_id, cell_id, tac, pci])

            if type(row[0]) is not float:
                date = Utils.strdate_to_postgredate(row[0])
            else:
                date = Utils.exceldate_to_postgredate(row[0])
            updata = row[8]
            downdata = row[9]
            sumdata = row[7]
            busi_lst.append([cell_name, date, updata, downdata, sumdata])

        return [info_lst, busi_lst]

    @timer
    def save_info_not_firsttime(self, info_lst):
        dbconn = self.connect_to_db()
        dbcursor = dbconn.cursor()

        dbcursor.execute("create TEMPORARY table tmp_info_4g("
                         "cell_name text NOT NULL,"
                         "base_name text,"
                         "base_id text,"
                         "cell_id text,"
                         "tac text,"
                         "pci text,"
                         "PRIMARY KEY (cell_name))")

        for info in info_lst:
            # print info
            try:
                dbcursor.execute("insert into tmp_info_4g (cell_name, base_name, base_id, cell_id, tac, pci)\
                                    values(%s, %s, %s, %s, %s, %s)", info)
            except (psycopg2.IntegrityError, psycopg2.InternalError) as e:
                print e

        dbcursor.execute("select cell_name from tmp_info_4g "
                         "except "
                         "select cell_name from cell_info_4g")
        names = dbcursor.fetchall()
        names_new = [name[0] for name in names]

        # print names
        print len(names_new), " new cells"  # , names_new

        for name in names_new:
            print name.decode("utf-8")
            dbcursor.execute("insert into cell_info_4g "
                             "select * from tmp_info_4g "
                             "where cell_name = '%s'" % name)

        dbconn.commit()
        dbconn.close()

    @timer
    def save_busi(self, busi_lst):
        dbconn = self.connect_to_db()
        dbcursor = dbconn.cursor()

        for busi in busi_lst:
            # print busi
            try:
                dbcursor.execute("insert into cell_busi_4g (cell_name, date, updata, downdata, alldata)\
                                    values(%s, %s, %s, %s, %s)", busi)
            except (psycopg2.IntegrityError, psycopg2.InternalError) as e:
                print e  # 如果出错则存储整个表的事务被回滚，进一步的处理有待研究
                #
        dbconn.commit()
        dbconn.close()

    def read_to_db(self):
        info_lst, busi_lst = self.read_excel()
        self.save_info_not_firsttime(info_lst)
        self.save_busi(busi_lst)



def test():
    # rf = Read2GFile("E:\projects\excel2DB\data\G网监控常用指标-20170101.xlsx".decode("utf-8").encode("GBK"))
    rf = Read3GFile("E:\projects\excel2DB\data\W网监控常用指标-20170310.xlsx".decode("utf-8").encode("GBK"))
    rf.read_to_db()

def testlte():
    rf = Read4GFile("E:\projects\excel2DB\data\LTE小区级日数据流量及忙时KPI指标备份_20170101.xlsx".decode("utf-8").encode("GBK"))
    rf.read_to_db()

def testgsm():
    rf = Read2GFile("E:\projects\excel2DB\data\G网监控常用指标-20170101.xls".decode("utf-8").encode("GBK"))

if __name__ == "__main__":
    #test()
    testlte()
    # a = '2017-01-01'
    # print a.split('-')
    # b = tuple(a.split('-'))
    # print psycopg2.Date(int(b[0]), int(b[1]), int(b[2]))
    #print *tuple(a.split('-'))
    # for i in xrange(2,5):
    #     print i
    #print datetime.datetime.now()