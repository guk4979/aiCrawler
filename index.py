from URLCollecter import getLinkList
from Search import Search
from PipeLine import PipeLine
import SelectImageUrl
import GetExLinks
import pymysql
import Rule
import Classify
from multiprocessing import Process, Lock
from os import listdir ,  mkdir

def Start():
    print("First crawling")
    for i in range(2):
        search = Search(i)
        url = search.search()

        internalLinks = getLinkList.getInLinks(url)
        SelectImageUrl.urlSelect(internalLinks) 
    PipeLine.DownloadCorrectImg()

def crawling():
    print("Crawling . .")
    lock = Lock()
    for i in range(5):
        exLinks = GetExLinks.getLinks(PipeLine.importData())
        PipeLine.insertData(exLinks)
        if i != 0:
            if i % 2 == 0:
                p = Process(target= PipeLine.DownloadIncorrectImg, args=(__name__,lock))
                p.start()
            if i % 5 == 0:
                classify()

def classify():
    Classify.classify()



if __name__ == '__main__':
    con = pymysql.connect(user=Rule.dbuser, passwd=Rule.dbpasswd, database=Rule.dbname ,host=Rule.dbhost, charset='utf8')
    cur = con.cursor()
    try:
        mkdir("./CorrectImages/{}".format(Rule.keyword))
    except FileExistsError:
        pass
    try:
        table_name = Rule.keyword
        sql = "CREATE TABLE {} (ID INT PRIMARY KEY AUTO_INCREMENT, URL TEXT NOT NULL, DOMAIN VARCHAR(100), IMPORT INT DEFAULT 0, DOWNLOAD INT DEFAULT 0, UNIQUE(URL(512)))".format(Rule.keyword)
        cur.execute(sql)
    except pymysql.err.OperationalError: 
        sql2 = "SELECT ID FROM {} WHERE DOMAIN=%s|%s".format(Rule.keyword)
        cur.execute(sql2, (Rule.seedDomain[0], Rule.seedDomain[1]))
        result = cur.fetchone()
        cur.close()
        if result != None:
            if listdir("./CorrectImages/{}".format(Rule.keyword)) == []:
                PipeLine.DownloadCorrectImg()
        else:
            Start()
    else:
        Start()

    crawling()
