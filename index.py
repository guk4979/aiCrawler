from URLCollecter import getLinkList
from Search import Search
import SelectImageUrl
import GetExLinks

if __name__ == '__main__':
    search = Search()
    url = search.search()
    print(url, "\n", "###"*3)

    internalLinks = getLinkList.getInLinks(url)
    externalLinks = getLinkList.getExLinks(url)

    if externalLinks != []:
        SelectImageUrl.urlSelect(externalLinks)

    getEx = GetExLinks.getLinks()
