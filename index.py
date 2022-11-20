from URLCollecter import getLinkList
from Search import Search
from PipeLine import PipeLine
import SelectImageUrl
import GetExLinks
import pymysql
import Rule
from multiprocessing import Process


def Start():
    for i in range(2):
        search = Search(i)
        url = search.search()

        internalLinks = getLinkList.getInLinks(url)
        SelectImageUrl.urlSelect(internalLinks) 

def crawling():
    for i in range(100):
        exLinks = GetExLinks.getLinks(PipeLine.importData)
        PipeLine.insertData(exLinks)
        i += 1
        # if i % 10 == 0:
        #     p = Process(target=)

def classify():
    pass

if __name__ == '__main__':
    con = pymysql.connect(user='crawler', passwd='1234', database='indexURL' ,host='localhost', charset='utf8')
    cur = con.cursor()
    try:
        table_name = Rule.keyword
        sql = "CREATE TABLE {} (ID INT PRIMARY KEY AUTO_INCREMENT, URL TEXT NOT NULL UNIQUE, DOMAIN VARCHAR(100), IMPORT INT DEFAULT 0)".format(Rule.keyword)
        cur.execute(sql)
    except pymysql.err.OperationalError: 
        sql2 = "SELECT ID FROM {} WHERE DOMAIN=%s|%s".format(Rule.keyword)
        cur.execute(sql2, (Rule.seedDomain[0], Rule.seedDomain[1]))
        result = cur.fetchone()
        cur.close()
        if result != None:
            PipeLine.DownloadCorrectImg()
        else:
            Start()
    else:
        Start()