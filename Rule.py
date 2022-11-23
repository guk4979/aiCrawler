from urllib.parse import urlparse
startUrl = ["https://www.google.co.kr","https://www.bing.com"]
searchUrl = None
keyword = "bj_코코"
seedDomain = [str(urlparse(startUrl[0]).netloc), str(urlparse(startUrl[1]).netloc)]
dbuser = "crawler"
dbpasswd = "1234"
dbname = "indexurl"