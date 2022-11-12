from multiprocessing.resource_sharer import stop
from urllib.parse import urlparse
import urllib.request
from urllib import error
from wsgiref import headers
from bs4 import BeautifulSoup
from time import sleep 
import re


class getUrl:

    def __init__(self, startingPage):
        header = {'User-Agent':'Chrome/106.0.0.0'}

        try:                              #타켓 커넥 예외 처리
            req = urllib.request.Request(startingPage, headers=header)
            html = urllib.request.urlopen(req)
        except error.HTTPError as err: 
            print(err.code)
            exit()
        self.bs = BeautifulSoup(html, 'html.parser')
        self.domain = urlparse(startingPage).netloc
        self.includeUrl = '{}://{}'.format(urlparse(startingPage).scheme, urlparse(startingPage).netloc)

    def getInternalLinks(self):
        includeUrl = '{}://{}'.format(urlparse(self.includeUrl).scheme, urlparse(self.includeUrl).netloc)
        internalLinks = []

        for link in self.bs.findAll('a', href= re.compile('^(/|.*' + includeUrl+ ')')):
            if link.attrs['href'] is not None:
                if link.attrs['href'] not in internalLinks:
                    if (link.attrs['href'].startswith('/')):
                        internalLinks.append(includeUrl+link.attrs['href'])
                    else:
                        internalLinks.append(link.attrs['href'])
        return internalLinks

    def getExternalLinks(self):
        externalLinks = []
        for link in self.bs.findAll('a', href=re.compile('^(http|www)((?!' + self.domain + ').)*$')):
            if link.attrs['href'] not in externalLinks:
                externalLinks.append(link.attrs['href'])
        
        return externalLinks

class getLinkList():

    def getInLinks(startPage): #외부 링크 리턴
        
        allIntLinks = []
        url = getUrl(startPage)
        internalLinks = url.getInternalLinks() 

        for link in internalLinks:
            if link not in allIntLinks:
                allIntLinks.append(link)
        
        return allIntLinks

    def getExLinks(startPage): #내부 링크 리턴
        allExtLinks = []
        url = getUrl(startPage)
        externalLinks = url.getExternalLinks()

        for link in externalLinks:
            if link not in allExtLinks:
                allExtLinks.append(link)

        return allExtLinks


