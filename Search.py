import Rule
from URLCollecter import getLinkList
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re

searchNameLists = ["p","q","query"]

class Search():

    def __init__(self,num) -> None:
        self.searchUrl = None
        self.num = num
        self.urlSelect(self.requestInUrl())

        if(self.searchUrl == None): #외부 url 요청
            print("No Found SearchUrl")
            print("Request External Url. . .")
            self.urlSelect(self.requestExUrl())
            if(self.searchUrl == None):
                print("No Found SearchUrl")
                exit()

    def urlSelect(self, urlLists): #검색엔진의 이미지 검색 url 찾기
        for url in urlLists:
            if(re.search("img|image", url)):
                self.searchUrl = url    

        print(self.searchUrl)

    def requestInUrl(self):
        return getLinkList.getInLinks(Rule.startUrl[self.num])

    def requestExUrl(self):
        return getLinkList.getExLinks(Rule.startUrl[self.num])

    def search(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.sel = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), chrome_options=options)
        self.sel.get(self.searchUrl)
        for name in searchNameLists:
            try:                
                self.elem = self.sel.find_element(By.NAME, name)
                break
            except: pass

        self.elem.send_keys(Rule.keyword + Keys.RETURN)
        url = self.sel.current_url
        self.sel.quit()
        return url