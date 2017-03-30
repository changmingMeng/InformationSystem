#! /usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import csv

from models import *

class control(object):

    @staticmethod
    def getListFromCSV(filepath):
        lst = []

        csvReader = csv.reader(file(filepath, 'rb'))
        for row in csvReader:
            for col in row:
                lst.append(col.decode("GBK").encode("utf-8"))

        return lst
#fn.SUM(CellBusi3G.erl), fn.SUM(CellBusi3G.updata)
    @classmethod
    def getZoneInfo(cls, begin_date, end_date, filepath):
        namelst = cls.getListFromCSV(filepath)
        sql = CellBusi3G.select(fn.SUM(CellBusi3G.erl), fn.SUM(CellBusi3G.updata), fn.SUM(CellBusi3G.downdata), fn.SUM(CellBusi3G.alldata))\
            .where((CellBusi3G.name << namelst)&(CellBusi3G.date.between(begin_date,end_date)))
        #sql = CellBusi3G.select().where(CellBusi3G.name << namelst).limit(50)
        return sql
def test(filepath):
    print control.getListFromCSV(filepath)
    ctl = control()
    sql = ctl.getZoneInfo("2017-03-01", "2017-03-02", filepath)
    if sql is not None:
        for t in sql:
            print t.erl, t.updata, t.downdata, t.alldata
    else:
        print "sql is None"

if __name__ == "__main__":
    test(r"E:\developtools\PyCharm 2016.3\projects\InformationSystem\files\test.csv")
