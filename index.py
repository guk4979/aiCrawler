from re import search
from URLCollecter import getLinkList
from Search import Search
import CorrectImage
import test

if __name__ == '__main__':
    search = Search()
    url = search.search()
    print(url, "\n", "###"*3)

    internalLinks = getLinkList.getInLinks(url)
    externalLinks = getLinkList.getExLinks(url)

    print(externalLinks, "\n", "###"*3)

    CorrectImage.urlSelect(externalLinks)

    test.getLinks()