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
        
    def search(self):
        # options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        # self.sel = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), chrome_options=options)
        # self.sel.get(self.searchUrl)
        # for name in searchNameLists:
        #     try:                
        #         self.elem = self.sel.find_element(By.NAME, name)
        #         break
        #     except: pass
        addition = ["/search?q={}&tbm=isch".format(Rule.keyword), "/images/search?q={}".format(Rule.keyword)]
        
        url = Rule.startUrl[self.num] + addition[self.num]

        return url