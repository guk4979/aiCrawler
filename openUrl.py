from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def openUrl(imageUrl):
    sel = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    sel.get(imageUrl)
    
    while(True):
        pass