from logging import exception
import re
import Rule

correctImage = []

def urlSelect(urlLists): #검색엔진의 이미지 검색 url 찾기
    if urlLists == ():
        print("no UrlLists")
        exit()

    for url in urlLists:
        if(re.search("img|images|{}".format(Rule.keyword), url)):
            correctImage.append(url)

    print(correctImage)
    return correctImage