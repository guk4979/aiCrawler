import pymysql
import shutil
import os
import Rule

con = pymysql.connect(user=Rule.dbuser, passwd=Rule.dbpasswd, database=Rule.dbname ,host='localhost', charset='utf8')
cur = con.cursor()
cur.execute("drop table {}".format(Rule.keyword))

shutil.rmtree('./IncorrectImages/{}'.format(Rule.keyword))
shutil.rmtree('./CorrectImages/{}'.format(Rule.keyword))
shutil.rmtree('./features/IncorrectImages/{}'.format(Rule.keyword))
shutil.rmtree('./features/CorrectImages/{}'.format(Rule.keyword))
