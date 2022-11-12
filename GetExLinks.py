import os
from multiprocessing import Pool
from URLCollecter import getLinkList
import Rule


def link(url):
    print(os.getpid(), url)
    linkList = getLinkList.getExLinks(url)
    print(os.getpid(), "End")
    return linkList

def getLinks(link):
    ExteranlUrlList = []
    print(len( "외부 링크 가져올 URL" ))
    print('pid of main:', os.getpid())
    p = Pool(5)
    data = p.map_async(link, "외부 링크 가져올 URL")
    for i in data.get():
        if i == None:
            break
        for j in i:
            ExteranlUrlList.append(j)
    p.close()
    p.join()
