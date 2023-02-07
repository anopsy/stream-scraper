
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from browsermobproxy import Server


url = "https://surfweer.nl/surf/webcam/"

#start proxy server
server = Server("/home/anopsy/stream-scraper/proxy/browsermob-proxy-2.1.4/bin/browsermob-proxy")
server.start()
proxy = server.create_proxy()

# selenium arguments
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("--proxy-server={0}".format(proxy.proxy))

caps = DesiredCapabilities.CHROME.copy()
caps['acceptSslCerts'] = True
caps['acceptInsecureCerts'] = True

proxy.new_har(ref=None,options={'captureHeaders': True,'captureContent':True,'captureBinaryContent': True}) # tag network logs 
              
driver = webdriver.Chrome('chromedriver',options=options,desired_capabilities=caps)
driver.get(url)

fetched = []
i=0
for ent in proxy.har['log']['entries']:
    i=i+1
    _url = ent['request']['url']
    _response = ent['response']
    
    #make sure havent already downloaded this piece
    if _url in fetched:
        continue
        
    if _url.endswith('.ts'):
        #check if this url had a valid response, if not, ignore it
        if 'text' not in _response['content'].keys() or not _response['content']['text']:
            continue
            
        print(_url+'\n')
        r1 = requests.get(_url, stream=True)
        if(r1.status_code == 200 or r1.status_code == 206):

            # re-open output file to append new video
            f = open("/home/anopsy/data/autodata/{}".format(i),"wb")
            data = b''
            for chunk in r1.iter_content(chunk_size=1024):
                if(chunk):
                    data += chunk
            f.write(data)
            f.close()
            fetched.append(_url)
        else:
            print("Received unexpected status code {}".format(r1.status_code))  