# encoding: utf-8

import os
import re
import xlrd
import psycopg2
import datetime
#import chardet
import logging

from utils import Utils
#import dbManip


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='import_db.log',
                    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

filename_key_2g = 'G网监控常用指标'.decode("utf-8").encode("GBK")
filename_key_3g = 'W网监控常用指标-'.decode("utf-8").encode("GBK")
filename_key_4g = 'LTE小区级日数据流量'.decode("utf-8").encode("GBK")


def timer(func):
    def warpper(*args, **kw):
        start = datetime.datetime.now()
        func(*args, **kw)
        end = datetime.datetime.now()
        print end-start
        #logging.DEBUG(end-start)
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
            sheet = workbook.sheet_by_index(1)#GSM话务文件的信息在第二张sheet
            print sheet.nrows
            #logging.DEBUG(sheet.nrows)
            # i =1
        for r in xrange(1,sheet.nrows):#excel第2行到最后一行
            row = sheet.row_values(r)
            if row[0]=="":
                continue
            # print i, row
            # i += 1
            name = row[1]
            lac = int(row[2])
            ci = int(row[3])
            bts = row[4]
            info_lst.append([name, lac, ci, bts])

            date = Utils.exceldate_to_postgredate(row[0])
            erl = row[5] if row[5] != "" else 0#把文件中空的列置零
            updata = row[7] if row[7] != "" else 0
            downdata = row[8] if row[8] != "" else 0
            sumdata = updata + downdata
            item = [name, date, erl, updata, downdata, sumdata]
            for i in range(len(item)):
                if item[i] == "":
                    item[i] = 0
            busi_lst.append(item)

        info_lst = Utils.lst_of_lst_distince_by_col(info_lst, 0)
        busi_lst = Utils.lst_of_lst_distince_by_col(busi_lst, 0)

        return [info_lst, busi_lst]

    @timer
    def save_info_not_firsttime(self, info_lst):
        dbconn = self.connect_to_db()
        dbcursor = dbconn.cursor()

        dbcursor.execute("create TEMPORARY table tmp_info_2g("
                         "name text NOT NULL,"
                         "lac text,"
                         "ci text,"
                         "bts text,"
                         "PRIMARY KEY (name))")

        for info in info_lst:
            # print info
            try:
                dbcursor.execute("insert into tmp_info_2g (name, lac, ci, bts)\
                                    values(%s, %s, %s, %s)", info)
            except (psycopg2.IntegrityError, psycopg2.InternalError) as e:
                print e
                #logging.INFO(e)

        dbcursor.execute("select name from tmp_info_2g "
                         "except "
                         "select name from cell_info_2g")
        names = dbcursor.fetchall()
        names_new = [name[0] for name in names]

        # print names
        print len(names_new), " new cells"  # , names_new

        for name in names_new:
            print name.decode("utf-8")
            #logging.INFO(name.decode("utf-8"))
            dbcursor.execute("insert into cell_info_2g "
                             "select * from tmp_info_2g "
                             "where name = '%s'" % name)

        dbconn.commit()
        dbconn.close()

    @timer
    def save_busi(self, busi_lst):
        dbconn = self.connect_to_db()
        dbcursor = dbconn.cursor()

        for busi in busi_lst:
            # print busi
            try:
                dbcursor.execute("insert into cell_busi_2g (name, date, erl, updata, downdata, alldata)\
                                    values(%s, %s, %s, %s, %s, %s)", busi)
            except (psycopg2.IntegrityError, psycopg2.InternalError) as e:
                print e  # 如果出错则存储整个表的事务被回滚，进一步的处理有待研究
                #logging.INFO(e)

        dbconn.commit()
        dbconn.close()

    def read_to_db(self):
        info_lst, busi_lst = self.read_excel()
        self.save_info_not_firsttime(info_lst)
        self.save_busi(busi_lst)

class Read3GFile(ReadExcelFile):


    #@timer
    def read_excel(self):
        info_lst = []
        busi_lst = []

        with xlrd.open_workbook(self.filename) as workbook:
            sheet = workbook.sheet_by_index(0)
            print sheet.nrows
            #logging.DEBUG(sheet.nrows)
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
            item = [name, date, erl, updata, downdata, sumdata]
            for i in range(len(item)):
                if item[i] == "":
                    item[i] = 0
            busi_lst.append(item)

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
                #logging.info(e)
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
                         "PRIMARY KEY (name))"
                         )

        for info in info_lst:
            #print info
            try:
                dbcursor.execute("insert into tmp_info_3g (name, lac, ci, nodeb, rnc, fac)\
                                values(%s, %s, %s, %s, %s, %s)",info)
            except (psycopg2.IntegrityError, psycopg2.InternalError) as e:
                print e
                #logging.info(e)

        dbcursor.execute("select name from tmp_info_3g "
                         "except "
                         "select name from cell_info_3g")
        names = dbcursor.fetchall()
        names_new = [name[0] for name in names]

        #print names
        print len(names_new), " new cells"#, names_new

        for name in names_new:
            print name.decode("utf-8")
            #logging.INFO(name.decode("utf-8"))
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
                #logging.INFO(e)

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

            name = row[2]
            base_name = row[1]
            base_id = int(row[3])
            cell_id = int(row[4])
            tac = int(row[5])
            pci = int(row[6])
            info_lst.append([name, base_name, base_id, cell_id, tac, pci])

            if type(row[0]) is not float:
                date = Utils.strdate_to_postgredate(row[0])
            else:
                date = Utils.exceldate_to_postgredate(row[0])
            updata = row[8]
            downdata = row[9]
            sumdata = row[7]
            erl = 0
            item = [name, date, erl, updata, downdata, sumdata]
            for i in range(len(item)):
                if item[i]=="":
                    item[i] = 0
            busi_lst.append(item)

        return [info_lst, busi_lst]

    @timer
    def save_info_not_firsttime(self, info_lst):
        dbconn = self.connect_to_db()
        dbcursor = dbconn.cursor()

        dbcursor.execute("create TEMPORARY table tmp_info_4g("
                         "name text NOT NULL,"
                         "base_name text,"
                         "base_id text,"
                         "cell_id text,"
                         "tac text,"
                         "pci text,"
                         "PRIMARY KEY (name))")

        for info in info_lst:
            # print info
            try:
                dbcursor.execute("insert into tmp_info_4g (name, base_name, base_id, cell_id, tac, pci)\
                                    values(%s, %s, %s, %s, %s, %s)", info)
            except (psycopg2.IntegrityError, psycopg2.InternalError) as e:
                print e

        dbcursor.execute("select name from tmp_info_4g "
                         "except "
                         "select name from cell_info_4g")
        names = dbcursor.fetchall()
        names_new = [name[0] for name in names]

        # print names
        print len(names_new), " new cells"  # , names_new

        for name in names_new:
            print name.decode("utf-8")
            dbcursor.execute("insert into cell_info_4g "
                             "select * from tmp_info_4g "
                             "where name = '%s'" % name)

        dbconn.commit()
        dbconn.close()

    @timer
    def save_busi(self, busi_lst):
        dbconn = self.connect_to_db()
        dbcursor = dbconn.cursor()

        for busi in busi_lst:
            # print busi
            try:
                dbcursor.execute("insert into cell_busi_4g (name, date, erl, updata, downdata, alldata)\
                                    values(%s, %s, %s, %s, %s, %s)", busi)
            except (psycopg2.IntegrityError, psycopg2.InternalError) as e:
                print e  # 如果出错则存储整个表的事务被回滚，进一步的处理有待研究
                #
        dbconn.commit()
        dbconn.close()

    def read_to_db(self):
        info_lst, busi_lst = self.read_excel()
        self.save_info_not_firsttime(info_lst)
        self.save_busi(busi_lst)

def import_excel(root, name):
    if re.search(filename_key_2g, name) != None:
        print "2G：", os.path.join(root, name).decode("GBK").encode("utf-8")
        try:
            rf = Read2GFile(os.path.join(root, name))
            rf.read_to_db()
        except:
            pass
    elif re.search(filename_key_3g, name) != None:
        print "3G：", os.path.join(root, name).decode("GBK").encode("utf-8")
        try:
            rf = Read3GFile(os.path.join(root, name))
            rf.read_to_db()
        except:
            pass
    elif re.search(filename_key_4g, name) != None:
        print "4G：", os.path.join(root, name).decode("GBK").encode("utf-8")
        try:
            rf = Read4GFile(os.path.join(root, name))
            rf.read_to_db()
        except:
            pass
    else:
        pass

def multi_import(dataroot, year = '2017'):
    '''循环遍历文件名并处理'''
    print dataroot
    for root, dirs, files in os.walk(dataroot):
        for name in files:
            #name = name.decode("GBK").encode("utf-8")
            if re.search(year, name) and (name.endswith(".xls") or name.endswith(".xlsx")):
                import_excel(root, name)

def multi_import_by_date(dataroot, date):
    '''date格式默认为datetime.date'''
    date_str = str(date).replace("-", "")

    for root, dirs, files in os.walk(dataroot):
        for name in files:
            if re.search(date_str, name):
                #name = name.decode("GBK").encode("utf-8")
                if name.endswith(".xls") or name.endswith(".xlsx"):
                    import_excel(root, name)
                    # if re.search(filename_key_2g, name) != None:
                    #     print "2G：", os.path.join(root, name).decode("GBK").encode("utf-8")
                    #     rf = Read2GFile(os.path.join(root, name))
                    #     rf.read_to_db()
                    # elif re.search(filename_key_3g, name) != None:
                    #     print "3G：", os.path.join(root, name).decode("GBK").encode("utf-8")
                    #     rf = Read3GFile(os.path.join(root, name))
                    #     rf.read_to_db()
                    # elif re.search(filename_key_4g, name) != None:
                    #     print "4G：", os.path.join(root, name).decode("GBK").encode("utf-8")
                    #     rf = Read4GFile(os.path.join(root, name))
                    #     rf.read_to_db()
                    # else:
                    #     pass

def multi_import_during_date(dataroot, begin_date, end_date):
    '''date格式默认为datetime.date'''
    #遍历begin_date和end_date之间的所有date
    date = begin_date
    while date <= end_date:
        print date
        multi_import_by_date(dataroot, date)
        date = date + datetime.timedelta(days=1)


def test():
    # rf = Read2GFile("E:\projects\excel2DB\data\G网监控常用指标-20170101.xlsx".decode("utf-8").encode("GBK"))
    rf = Read3GFile(r"F:\36服务器搬迁资料\02-外部共享\23-2014年WCDMA日常作业计划\话务量&流量指标月备份\2017\W网监控常用指标-20170114.xlsx".decode("utf-8").encode("GBK"))
    rf.read_to_db()

def testlte():
    rf = Read4GFile(r"F:\36服务器搬迁资料\02-外部共享\22-2014年LTE日常作业计划\华为\LTE小区级日数据流量及忙时KPI指标备份\2017\5月\LTE小区级日数据流量及忙时KPI指标_20170508.xlsx".decode("utf-8").encode("GBK"))
    rf.read_to_db()

def testgsm():
    rf = Read2GFile("E:\projects\excel2DB\data\G网监控常用指标-20170102.xls".decode("utf-8").encode("GBK"))
    #rf = Read2GFile("E:\projects\excel2DB\data\data.xls".decode("utf-8").encode("GBK")
    rf.read_to_db()

if __name__ == "__main__":
    #multi_import("F:\36服务器搬迁资料\02-外部共享\23-2014年WCDMA日常作业计划\话务量&流量指标月备份")
    #multi_import_during_date("dataroot",datetime.date(2017,3,1), datetime.date(2017,4,30))
    testlte()