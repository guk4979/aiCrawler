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

poolcount = 10
class FeatureExtractor:
  def __init__(self):
      # Use VGG-16 as the architecture and ImageNet for the weight
      base_model = VGG16(weights='imagenet')
      # Customize the model to return features from fully-connected layer
      self.model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)

  def extract(self, img):
      # Resize the img
      img = img.resize((224, 224))
      # Convert the img color space
      img = img.convert('RGB')
      # Reformat the img
      x = utils.img_to_array(img)
      x = np.expand_dims(x, axis=0)
      x = preprocess_input(x)
      # Extract Features
      feature = self.model.predict(x)[0]
      return feature / np.linalg.norm(feature)

class PipeLine:

    def insertData(urls):
        con = pymysql.connect(user=Rule.dbuser, passwd=Rule.dbpasswd, database=Rule.dbname ,host='localhost', charset='utf8')
        cur = con.cursor()
        sql = 'INSERT INTO {} (URL, DOMAIN) VALUES( %s, %s)'.format(Rule.keyword)
        for url in urls:
            try:
                cur.execute(sql , (url, urlparse(url).netloc))
            except pymysql.err.IntegrityError:
                pass
        con.commit()

    def importData():
        con = pymysql.connect(user=Rule.dbuser, passwd=Rule.dbpasswd, database=Rule.dbname ,host='localhost', charset='utf8')
        cur = con.cursor()
        sql = 'SELECT URL FROM {} WHERE IMPORT=0'.format(Rule.keyword)
        cur.execute(sql)
        result = [item[0] for item in cur.fetchall()[:5]]
        if result == None:
            cur.close()
            importData()
        sql3 = "SELECT ID FROM {} WHERE URL='{}'".format(Rule.keyword, result[-1])
        cur.execute(sql3)
        last_id = cur.fetchone()

        sql2 = 'UPDATE {} SET IMPORT=1 WHERE IMPORT=0 AND ID <= {}'.format(Rule.keyword, last_id[0])
        cur.execute(sql2)
        con.commit()
        return result

    def DownloadCorrectImg():
        con = pymysql.connect(user=Rule.dbuser, passwd=Rule.dbpasswd, database=Rule.dbname ,host='localhost', charset='utf8')
        cur = con.cursor()
        sql = "SELECT URL FROM {} WHERE DOMAIN=%s|%s AND DOWNLOAD = 0".format(Rule.keyword)
        cur.execute(sql,(Rule.seedDomain[0], Rule.seedDomain[1]))
        # sql2 = 'UPDATE {} SET DOWNLOAD=1 WHERE DOMAIN=%s|%s AND DOWNLOAD=0'.format(Rule.keyword)
        # cur.execute(sql2,(Rule.seedDomain[0], Rule.seedDomain[1]))
        result = [item[0] for item in cur.fetchall()]
        con.close()
        downloadimg("Correct",result)
        
    def DownloadIncorrectImg(name, lock):
        lock.acquire()
        con = pymysql.connect(user=Rule.dbuser, passwd=Rule.dbpasswd, database=Rule.dbname ,host='localhost', charset='utf8')
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
    try:
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
    except Exception:
        return
    if status == 'Correct':
        imgList = imgList[:5]
    else: imgList = imgList[:100]
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
        name = avoidDuplication(img_path, feature_path ,i)
        path = img_path + "/" + str(name) + ".jpg"
        fe_path = feature_path + "/" + str(name) + ".npy"
        try:
            request.urlretrieve(imgurl,path)
        except HTTPError:
            pass
        except UnicodeEncodeError:
            pass
        except Exception:
            pass
        else:

            try:
                Image.open(path)
            except UnidentifiedImageError:
                print("unidentify")
                os.remove(path)
            else:
                img = Image.open(path)
                if img.size[0] <= 100:
                    img.close()
                    os.remove(path)
                else:
                    try:
                        feature = fe.extract(img)
                        np.save(fe_path, feature)
                    except Exception as e:
                        img.close()
                        os.remove(path)
                    else:
                        if not os.path.exists(fe_path):
                            img.close()
                            os.remove(path)
                            os.remove(fe_path)
    
    print("{}images 다운로드 끝".format(status))

def avoidDuplication(path,fet_path,num):
  i = num
  while os.path.exists(path + "/" + str(i) + ".jpg") | os.path.exists(fet_path + "/" + str(i) + ".npy"):
    i += 1
  return i


def findSrc(url):
    header = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
    url = url.replace(" ", "%20")
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
        for link in bs.findAll('img', src=re.compile('^http')):
            if link.attrs['src'] is not None:
                if link.attrs['src'] not in temp:
                    temp.append(link.attrs['src'])
        return temp