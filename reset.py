import pymysql
import shutil
import os
import Rule

try:
    con = pymysql.connect(user=Rule.dbuser, passwd=Rule.dbpasswd, database=Rule.dbname ,host='localhost', charset='utf8')
    cur = con.cursor()
    cur.execute("drop table {}".format(Rule.keyword))
except:
    pass
    
try:
    shutil.rmtree('./IncorrectImages/{}'.format(Rule.keyword))
except FileNotFoundError:
    pass
try:
    shutil.rmtree('./CorrectImages/{}'.format(Rule.keyword))
except FileNotFoundError:
    pass
try:
    shutil.rmtree('./features/IncorrectImages/{}'.format(Rule.keyword))
except FileNotFoundError:
    pass
try:
    shutil.rmtree('./features/CorrectImages/{}'.format(Rule.keyword))
except FileNotFoundError:
    pass
    