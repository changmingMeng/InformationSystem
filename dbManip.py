# coding: utf-8

import psycopg2
import utils
class dbManipulate(object):
    def __init__(self,
                 database = "testdb",
                 user = "postgres",
                 password = "123456",
                 host = "127.0.0.1",
                 port = "5432"):
        self.conn = psycopg2.connect(database = database,
                                     user = user,
                                     password = password,
                                     host = host,
                                     port = port)

    def __del__(self):
        #self.Commit()
        self.conn.close()
        print "one dbm ended"
    def Insert(self, ID, date, time, erl, updata, downdata, alldata, netType):
        cursor = self.conn.cursor()
        post = [ID, date, time, erl, updata, downdata, alldata, netType]
        try:
            cursor.execute("insert into cell_data (ID, date, time, erl, updata, downdata, alldata, netType)\
                            values(%s, %s, %s, %s, %s, %s, %s, %s)",
                            post)
            return True
        except psycopg2.IntegrityError, msg:
            return False
        except psycopg2.InternalError, msg:
            return False


    def InsertWithCommitEach(self, ID, date, time, erl, updata, downdata, alldata, netType):
        cursor = self.conn.cursor()
        post = [ID, date, time, erl, updata, downdata, alldata, netType]
        try:
            cursor.execute("insert into cell_data (ID, date, time, erl, updata, downdata, alldata, netType)\
                                    values(%s, %s, %s, %s, %s, %s, %s, %s)",
                           post)
        except psycopg2.IntegrityError, msg:
            pass
        except psycopg2.InternalError, msg:
            pass
        finally:
            self.conn.commit()

    def Update(self, ID, dataName, data):
        cursor = self.conn.cursor()
        newData = self.DataDecorate(data)
        #当传入的data是字符串时，将其装换成r"'data'"的格式以便在update拼接后的格式正确
        #当传入的data不是字符串时，将其转换成字符串
        update = "UPDATE cell_data SET " + dataName + " = " + newData + " WHERE id = '" + ID + "'"
        #print update
        cursor.execute(update)
        #self.conn.commit()

    def UpdateByCondition(self, dataName, data, **condition):
        cursor = self.conn.cursor()
        newData = self.DataDecorate(data)
        update = "UPDATE cell_data SET " + dataName + " = " + newData
        ck = condition.keys()
        for index, key in enumerate(ck):
            if index == 0:
                update += " where " + key + "='" + condition[key] + "'"
            else:
                update += " and " + key + "='" + condition[key] + "'"
        #print update
        cursor.execute(update)

    def SelectAllByID(self, ID):
        cursor = self.conn.cursor()
        select = "select * from cell_data where id = '" + ID + "'"
        cursor.execute(select)
        return cursor.fetchall()

    def SelectDataByCondition(self, dataType, inputID, inputDate, inputTime):
        return self.SelectItemByCondition(dataType, ID=inputID, date=inputDate, time=inputTime)

    def SelectItemByCondition(self, item, **condition):
        cursor = self.conn.cursor()
        select = "select " + item + " from cell_data"
        ck = condition.keys()
        for index, key in enumerate(ck):
            if index == 0:
                select += " where " + key + "='" + condition[key] + "'"
            else:
                select += " and " + key + "='" + condition[key] + "'"
        cursor.execute(select)
        return cursor.fetchone()[0]

    def SelectAllByCondition(self, **condition):
        cursor = self.conn.cursor()
        select = "select * from cell_data"
        ck = condition.keys()
        for index, key in enumerate(ck):
            if index == 0:
                select += " where " + key + "='" + condition[key] + "'"
            else:
                select += " and " + key + "='" + condition[key] + "'"
        cursor.execute(select)
        return cursor.fetchall()

    def IsHaveID(self, ID):
        return not self.SelectAllByID(ID) == []

    def IsHaveRow(self, inputID, inputDate, inputTime):
        return not self.SelectAllByCondition(ID=inputID, date=inputDate, time=inputTime) == []




    def DataDecorate(self, data):
        ut = utils.Utils()
        if ut.IsStringLike(data):
            return "'" + data + "'"
        else:
            return str(data)

    def Commit(self):
        self.conn.commit()
def a():
    b = []
    for bb in b:
        print "b"

if __name__ == "__main__":
    #conn = psycopg2.connect("testdb,"")
    test = dbManipulate()
    #print test.SelectAllByID("4600125046183")
    #print test.SelectItemByID("4600125046183", "date")
    #post = {ID=4600125046183, date=2016-11-28}
    print test.IsHaveRow("46001250CA5FD", "2016-11-28", "22:00:00")
    #print test.SelectItem(ID="46001250CA5FD", date="2016-11-29", time="22:00:00")
    #test.Insert('10010', psycopg2.Date(2016, 12, 9), psycopg2.Time(11, 29, 00), 1234.56, 23456789.12, 56789012.34, 890123456.78, "2G")
    #print test.IsHaveID("10000")
    #test.Update("10010", "nettype", "4G")