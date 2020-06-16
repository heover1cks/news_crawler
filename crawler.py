import requests
import pdb
import json
import timeit
import datetime as dt
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from pymongo import MongoClient
#import boto3
import os

from base64 import b64decode

QUERY_STRS=['클라우드','구글','마이크로스프트','아마존','오픈소스']

ROOT_PATH="https://search.naver.com/search.naver?where=news&sm=tab_opt&sort=0&photo=3&field=0&reporter_article=&pd=4&ds=&de=&docid=&d=1"
QUERY="&query="
START="&start="
TODAY= dt.date.today().strftime("%Y%m%d")

MONGO_URI = ""

pages = 10
addedCount = 0

#Requests Option
headers = {'Content-Type': 'application/json; charset=utf-8','User-Agent':'Chrome/39.0.2171.95'}

#Selenium Option
options = webdriver.ChromeOptions()
options.add_argument('headless')
#driver = webdriver.Chrome('/Users/jaeyoungheo/workspace/crawling/chromedriver',options=options)
#driver.implicitly_wait(3)



def get_data(url):
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        response_body = response.text
        print(json.loads(response_body))
        return json.loads(response_body)
    else:
        print('Error Code: '+response.status_code)

# def get_coordinate(addr):
#     url = API_HOST + PATH + addr
#     #headers['Authorization']=APP_KEY_DECRYPTED
#     response = requests.get(url,headers=headers)
#     rescode = response.status_code
#     if rescode == 200:
#         response_body = response.text
#         return json.loads(response_body)#.get('documents')
#     else:
#         print('Error Code:' + rescode)

# def post(url,data):
#     dataHeaders = {'Content-Type': 'application/json; charset=utf-8','User-Agent':'Chrome/39.0.2171.95','Accept':'application/json'}
#     jsonData = json.dumps(data)
#     response = requests.post(url,data=jsonData,headers=dataHeaders)
#     result = response.status_code
#     #print(result)

if __name__ == "__main__":
    client = pymongo.MongoClient(MONGO_URI)
    start = timeit.default_timer()
    current_list = []#get_data(Data_URL_DECRYPTED)
    for query in QUERY_STRS:
        print('Query String Changing')
        print('Query: '+query)
        for page in range(pages):
            print('Page Changing')
            req = requests.get(ROOT_PATH+QUERY+query+START+str(1+10*page), headers=headers)
            status = req.status_code
            is_ok = req.ok

            soup = bs(req.text,'html.parser')
            refs = soup.find('ul',class_='type01')#select('main_content > div.list_body.newsflash_body > ul.type06_headline > li > dl > dt:nth-child(2) > a')\
            

            try:
                for ref in refs:
                    #print(ref)
                    data = {} 
                    try:
                        article_title = ref.find('a',class_='_sp_each_title').get('title')#.get_text().split('\n')[0]
                        article_href = ref.find('a',class_='_sp_each_url').get('href')#.select('dl > dd > a').get('href')
                        article_source = ref.find('span',class_='_sp_each_source').get_text()#.select('dl > dd > a').get('href')
                        # print(article_title)
                        # print(article_href)
                        # print(article_source)
                        
                        #pdb.set_trace()
                        cur_article = requests.get(article_href,headers=headers)
                        cur_soup = bs(cur_article.text,'html.parser')
                        cur_date = cur_soup.find('span', class_='t11').get_text()
                        cur_body = cur_soup.find('div',id='articleBodyContents').get_text().strip()
                        # print(cur_date)
                        # print(cur_body)

                        data['category'] = query
                        data['article_title'] = article_title
                        data['article_href'] = article_href
                        data['article_source'] = article_source
                        data['article_date'] = cur_date
                        data['article_body'] = cur_body
                        
    
                        if next((item for item in current_list if item['article_title'] == data.get('article_title')),False):
                            print("Duplicated: "+data.get('article_title'))
                        else:
                            #post(data_url,data)
                            current_list.append(data)
                            print(data)
                            addedCount += 1
                            print("Newly Added/count:"+str(addedCount))
                    except:
                        pass
                    #pdb.set_trace()
                    print('='*20)
            except:
                pass
    tot_time = timeit.default_timer()-start
    print(current_list)
    print("Execution Time: "+str(tot_time))
    print("Total Articles: "+str(addedCount))
