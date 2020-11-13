import requests 
import urllib
import os
import re
import json
import datetime
import pandas
import time
import shutil
from urllib.parse import urlparse
from bs4 import BeautifulSoup


with open('./CrawList.txt',encoding='utf-8') as page_file:
    pageList = (line.rstrip() for line in page_file) 
    pageList = list(line for line in pageList if line)

dirPath = './Img/'
if not os.path.isdir(dirPath):
    os.mkdir(dirPath)

for name in pageList:
    
    print(name)

    dataPath = './Analysize/'
    pkl = pandas.read_pickle(dataPath+name+'.pkl')
    link = pkl['Img link']
    postID = pkl['Post ID']
    checkList = []
    dirPath='./Img/'+name

    if not os.path.isdir(dirPath):
        os.mkdir(dirPath)
    else:
        checkList = os.listdir(dirPath)

    for i in range(len(link)):
        imglink = link[i].split('\n')

        for j in imglink:

            if j == '':
                continue
            
            picname = j.split('?')[0].split('/')[-1]

            #Quote img is .php
            if(j.find('safe_image.php')!=-1):
                picname = 'Quote-'+postID[i]+'.jpg'

            print(picname)
            if checkList != []:
                if str(checkList).find(picname)!=-1:
                    print("exist")
                    continue

            r = requests.get(j,stream = True)
                
            with open(dirPath+'/'+picname, 'wb') as img:
                shutil.copyfileobj(r.raw, img)