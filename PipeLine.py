import pymysql
import Rule
from urllib.parse import urlparse
from multiprocessing import Pool
from bs4 import BeautifulSoup
from urllib import request
from urllib.error import HTTPError, URLError
from PIL import Image, UnidentifiedImageError
import os
import re

poolcount = 15

class PipeLine:

    def insertData(urls):
        con = pymysql.connect(user='crawler', passwd='1234', database='indexURL' ,host='localhost', charset='utf8')
        cur = con.cursor()
        sql = 'INSERT INTO {} (URL, DOMAIN) VALUES( %s, %s)'.format(Rule.keyword)
        for url in urls:
            try:
                cur.execute(sql , (url, urlparse(url).netloc))
            except pymysql.err.IntegrityError:
                pass
        con.commit()

    def importData():
        con = pymysql.connect(user='crawler', passwd='1234', database='indexURL' ,host='localhost', charset='utf8')
        cur = con.cursor()
        sql = 'SELECT * FROM {} WHERE IMPORT=0'.format(Rule.keyword)
        cur.execute(sql)
        result = [item[0] for item in cur.fetchall()]
        sql2 = 'UPDATE {} SET IMPORT=1, WHERE IMPORT=0'.format(Rule.keyword)
        cur.execute(sql2)
        return result

    def DownloadCorrectImg():
        con = pymysql.connect(user='crawler', passwd='1234', database='indexURL' ,host='localhost', charset='utf8')
        cur = con.cursor()
        sql = "SELECT URL FROM {} WHERE DOMAIN= %s|%s".format(Rule.keyword)
        cur.execute(sql, (Rule.seedDomain[0], Rule.seedDomain[1]))
        result = [item[0] for item in cur.fetchall()]
        downloadimg("Correct",result)
        
    def DownloadIncorrectImg():
        con = pymysql.connect(user='crawler', passwd='1234', database='indexURL' ,host='localhost', charset='utf8')
        cur = con.cursor()
        sql = "SELECT URL FROM {} WHERE DOMAIN != %s|%s".format(Rule.keyword)
        cur.execute(sql, (Rule.seedDomain[0], Rule.seedDomain[1]))
        result = [item[0] for item in cur.fetchall()]
        downloadimg("Incorrect",result)

def downloadimg(status,result):
    imgList = []
    p = Pool(poolcount)
    data = p.map_async(findSrc, result)
    p.close()
    p.join()

    for i in data.get():
        if type(i) == list:
            for j in i:
                if j is not None:
                    if j not in imgList:
                        imgList.append(j)
        else: 
            if i is not None:
                if i not in imgList:
                    imgList.append(i)

    opener=request.build_opener()
    opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36')]
    request.install_opener(opener)
    i = 0
    path = "./{}Images/{}".format(status,Rule.keyword)
    if not os.path.exists(path):
        os.mkdir(path)
    for imgurl in imgList:
        try:
            request.urlretrieve(imgurl,path + "/" + str(i) + ".jpg")
            try:
                Image.open(path + "/" + str(i) + ".jpg")
            except UnidentifiedImageError:
                print("unidentify")
            else:
                if Image.open(path + "/" + str(i) + ".jpg").size[1] <= 100:
                    os.remove(path + "/" + str(i) + ".jpg")
                else:
                    i += 1
        except HTTPError:
            pass



def findSrc(url):
    header = {'User-Agent':'Chrome/106.0.0.0'}
    try:                              #타켓 커넥 예외 처리
        req = request.Request(url, headers=header)
        html = request.urlopen(req)
    except HTTPError: 
        pass
    except URLError:
        pass
    else:
        temp = []
        bs = BeautifulSoup(html, "html.parser")
        for link in bs.findAll('img', src=re.compile('^(http|data)')):
            if link.attrs['src'] is not None:
                if link.attrs['src'] not in temp:
                    temp.append(link.attrs['src'])
        return temp
