import os
from multiprocessing import Process, Queue, Pool
from URLCollecter import getLinkList
import CorrectImage
import Rule


def link(url):
    print(os.getpid())
    # linkList = getLinkList.getExLinks(url)
    linkList = [1,2,3,4,5]
    global externalLinks
    for i in linkList:
        externalLinks.put(i)
    # q.put(url)


externalLinks = Queue()

def getLinks():
    print(len(CorrectImage.correctImage))
    print('pid of main:', os.getpid())
    global externalLinks
    p = Pool(5)
    p.map(link, CorrectImage.correctImage)
    p.close()
    p.join()

    print("This is RESULT:",externalLinks.get())
    