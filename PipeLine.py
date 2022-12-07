import pymysql
import Rule
from urllib.parse import urlparse
from multiprocessing import Pool
from bs4 import BeautifulSoup
from urllib import request
from urllib.error import HTTPError, URLError
from PIL import Image, UnidentifiedImageError
from keras import utils
from keras.applications.vgg16 import VGG16, preprocess_input
from keras.models import Model
from keras.layers import Concatenate
import numpy as np
import socket
import os
import re

poolcount = 5

class FeatureExtractor:
  def __init__(self):
      # Use VGG-16 as the architecture and ImageNet for the weight
      base_model = VGG16(weights='imagenet')
      # Customize the model to return features from fully-connected layer
      self.model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)

  def extract(self, img):
      # Resize the image
      img = img.resize((224, 224))
      # Convert the image color space
      img = img.convert('RGB')
      # Reformat the image
      x = utils.img_to_array(img)
      x = np.expand_dims(x, axis=0)
      x = preprocess_input(x)
      # Extract Features
      feature = self.model.predict(x)[0]
      return feature / np.linalg.norm(feature)

class PipeLine:

    def insertData(urls):
        con = pymysql.connect(user=Rule.dbuser, passwd=Rule.dbpasswd, database=Rule.dbname ,host=Rule.dbhost, charset='utf8')
        cur = con.cursor()
        sql = 'INSERT INTO {} (URL, DOMAIN) VALUES( %s, %s)'.format(Rule.keyword)
        for url in urls:
            try:
                cur.execute(sql , (url, urlparse(url).netloc))
            except pymysql.err.IntegrityError:
                pass
        con.commit()

    def importData():
        con = pymysql.connect(user=Rule.dbuser, passwd=Rule.dbpasswd, database=Rule.dbname ,host=Rule.dbhost, charset='utf8')
        cur = con.cursor()
        sql = 'SELECT URL FROM {} WHERE IMPORT=0'.format(Rule.keyword)
        cur.execute(sql)
        result = [item[0] for item in cur.fetchall()[:10]]
        sql3 = "SELECT ID FROM {} WHERE URL='{}'".format(Rule.keyword, result[9])
        cur.execute(sql3)
        last_id = cur.fetchone()

        sql2 = 'UPDATE {} SET IMPORT=1 WHERE IMPORT=0 AND ID <= {}'.format(Rule.keyword, last_id[0])
        cur.execute(sql2)
        con.commit()
        return result

    def DownloadCorrectImg():
        con = pymysql.connect(user=Rule.dbuser, passwd=Rule.dbpasswd, database=Rule.dbname ,host=Rule.dbhost, charset='utf8')
        cur = con.cursor()
        sql = "SELECT URL FROM {} WHERE DOMAIN=%s|%s AND DOWNLOAD = 0".format(Rule.keyword)
        cur.execute(sql,(Rule.seedDomain[0], Rule.seedDomain[1]))
        # sql2 = 'UPDATE {} SET DOWNLOAD=1 WHERE DOMAIN=%s|%s AND DOWNLOAD=0'.format(Rule.keyword)
        # cur.execute(sql2,(Rule.seedDomain[0], Rule.seedDomain[1]))
        result = [item[0] for item in cur.fetchall()]
        con.close()
        downloadimg("Correct",result)
        
    def DownloadIncorrectImg(name,lock):
        lock.acquire()
        con = pymysql.connect(user=Rule.dbuser, passwd=Rule.dbpasswd, database=Rule.dbname ,host=Rule.dbhost, charset='utf8')
        cur = con.cursor()
        sql = "SELECT URL FROM {} WHERE DOWNLOAD = 0".format(Rule.keyword)
        cur.execute(sql)
        result = [item[0] for item in cur.fetchall()]
        
        sql = 'UPDATE {} SET DOWNLOAD=1 WHERE DOWNLOAD=0'.format(Rule.keyword)
        cur.execute(sql)
        con.commit()
        downloadimg("Incorrect",result)
        lock.release()

def downloadimg(status,result):
    print("{}images 다운로드 시작".format(status))
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
    if status == 'Correct':
        imgList = imgList[:5]
    opener=request.build_opener()
    opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36')]
    request.install_opener(opener)
    fe = FeatureExtractor()
    i = 0
    img_path = "./{}Images/{}".format(status,Rule.keyword)
    feature_path = "./features/{}Images/{}".format(status,Rule.keyword)
    if not os.path.exists(img_path):
        os.mkdir(img_path)
    if not os.path.exists(feature_path):
        os.mkdir(feature_path)
    for imgurl in imgList:
        try:
            name = avoidDuplication(img_path, feature_path ,i)
            path = img_path + "/" + str(name) + ".jpg"
            fe_path = feature_path + "/" + str(name) + ".npy"
            request.urlretrieve(imgurl,path)
            try:
                Image.open(path)
            except UnidentifiedImageError:
                print("unidentify")
                os.remove(path)
            else:
                if Image.open(path).size[1] <= 100:
                    os.remove(path)
                # if img = Image.open(path).size[1] <= 300:
                    
                else:
                    try:
                        feature = fe.extract(Image.open(path))
                        np.save(fe_path, feature)
                    except Exception as e:
                        os.remove(path)
                        os.remove(fe_path)
                    if not os.path.exists(fe_path):
                        os.remove(path)
                        os.remove(fe_path)
                    
        except HTTPError:
            pass
        except UnicodeEncodeError:
            pass
    
    print("{}images 다운로드 끝".format(status))

def avoidDuplication(path,fet_path,num):
  i = num
  while os.path.exists(path + "/" + str(i) + ".jpg") | os.path.exists(fet_path + "/" + str(i) + ".npy"):
    i += 1
  return i


def findSrc(url):
    header = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
    try:                              #타켓 커넥 예외 처리
        socket.setdefaulttimeout(5)
        req = request.Request(url, headers=header)
        html = request.urlopen(req)
        
    except HTTPError: 
        print("HTTPSError")
    except URLError:
        print("URLError")
    except UnicodeDecodeError:
        print("UnicodeDecodeError")
    except Exception as e:
        print(e)
    else:
        temp = []
        bs = BeautifulSoup(html, "html.parser")
        print(url)
        
        if request.urlparse(url).netloc == Rule.seedDomain[0]:
            pa = bs.find('div', jsname = 'V7lXsd')
            print('pa:', pa)
            if pa == None:
                pa = bs
            for link in pa.findAll('img', src=re.compile('^http')):
                if link.attrs['src'] is not None:
                    if link.attrs['src'] not in temp:
                        temp.append(link.attrs['src'])
        else:
            for link in bs.findAll('img', src=re.compile('^http')):
                if link.attrs['src'] is not None:
                    if link.attrs['src'] not in temp:
                        if re.search('bing', urlparse(link.attrs['src']).netloc):
                            src = link.attrs['src'].split('?')
                            temp.append(src[0])
                        else:
                            temp.append(link.attrs['src'])
        return temp