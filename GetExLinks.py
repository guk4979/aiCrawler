import os
from multiprocessing import Pool
from URLCollecter import getLinkList


def links(url):
    linkList = getLinkList.getExLinks(url)
    
    return linkList

def getLinks(link):
    ExteranlUrlList = []
    print('pid of main:', os.getpid())
    p = Pool(10)
    data = p.map_async(links, link)
    for i in data.get():
        if i == None:
            break
        for j in i:
            ExteranlUrlList.append(j)
    p.close()
    p.join()

    return ExteranlUrlList
