import re
import Rule
from PipeLine import PipeLine


def urlSelect(urlLists): #검색엔진의 이미지 검색 url 찾기
    urls = []
    for url in urlLists:
        if(re.search("(img|images|{})".format(Rule.keyword), url)):
            urls.append(url)

    PipeLine.insertData(urls)
    # getImageUrl(url)

# def getImageUrl(url):
#     imgURL = []
#     for link in bs.findAll('img', src=re.compile('^(http|www)((?!' + domain + ').)*$')):
#             if link.attrs['href'] is not None:
#                 if link.attrs['href'] not in externalLinks:
#                     externalLinks.append(link.attrs['href'])