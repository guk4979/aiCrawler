from pymysql.err import OperationalError
import pymysql
import Rule
import re


con = pymysql.connect(user='crawler', passwd='1234', database='indexURL' ,host='localhost', charset='utf8')
cur = con.cursor(pymysql.cursors.DictCursor)
table_name = Rule.keyword
try:
    cur.execute("CREATE TABLE {} (ID(int))".format(table_name))
except OperationalError:
    cur.execute('')


# result = cur.fetchall()
# if len(cur.fetchall()) == 1:
#     print('sucess')
