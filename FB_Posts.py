import json
import requests
import urllib
from bs4 import BeautifulSoup
import re
import time
import os,sys
import random
import datetime
import shutil

def get_fbid(fb_name):
    URL = "https://www.facebook.com/"+fb_name
    r = requests.get(url = URL)
    try:
        pageid = re.search(r'fb://page/\?id=(.*?)"', r.text).group(1)
        return pageid
    except:
        return 0

#IMPORTANT
########################################
headers = {
    'user-agent': 'Chrome/84.0.4147.89'
}

cookies = { #put cookie may solve some problem when crawling
    'cookie': ''
}

url = 'https://www.facebook.com/pages_reaction_units/more/'

payloads = {
    'page_id': '',
    'cursor': '{"timeline_cursor":"","timeline_section_cursor":{},"has_next_page":true}',
    'surface': 'www_pages_posts',
    'unit_count': '8',
    'fd_referrer_ui_surface': 'external',
    'fb_dtsg_ag': '',
    '__user': '0',
    '__a': '1'
}
########################################

#Facebook time
timezone = 54000

with open('./CrawList.txt',encoding='utf-8') as page_file:
    pageList = (line.rstrip() for line in page_file) 
    pageList = list(line for line in pageList if line)

dirPath = "./json_Data/"
if not os.path.isdir(dirPath):
    os.mkdir(dirPath)
    
for i in pageList:
    payload = dict(payloads)
    pageid = 0
    num = 0
    timecount = 0
    fbname = i
    html = ''
    error_code = 0
    contentlen = None
    #Year Set (change it if you want)
    setyear = 2020
    
    #Path (change it if you dont have D slot)
    dirPath = "./json_Data/" + fbname + '/'
    ErrorPath = './Error/'

    pageid = get_fbid(fbname)
    payload['page_id'] = pageid
    
    print('Crawling '+fbname)

    if(pageid==0):
        print('No Page id, try next one')
        continue 

    if os.path.isdir(dirPath):
        
        print(fbname+"\nDict exists, checking")
        countfile = os.listdir(dirPath)
        if(len(countfile)>0):
            countfile.sort(key=lambda f: int(re.sub('\D','', f)))
            print("Last json: "+str(countfile[-1]))
            cursor = open(dirPath+str(countfile[-1]),'r',encoding='utf-8').read()
            date = cursor
            try:
                cursor = re.search(r'cursor=(.*?)&amp;surface', cursor.encode().decode('unicode-escape')).group(1)
                cursor = urllib.parse.unquote(cursor)
                payload['cursor']=cursor
                num = int(str(countfile[-1]).replace(".json",""))+1
            except:
                continue
            
            date = re.findall(r'data-utime=\\\"(\d+.*?)\\\"', date)
            try:
                date = int(date[-1])
                date = datetime.datetime.fromtimestamp(date-timezone).year
                if(date<=setyear):
                    print("json Year <= Set Year")
                    continue
            except:
                print("No Date in file")
        else:
            print("Dict empty, continue")
    else:
        os.mkdir(dirPath) 
    
    

    while True:
        ##################
        r = requests.get(url,params = payload, headers = headers,cookies = cookies)
        
        if((r.status_code)!=200):
            print("status code error"+str(r.status_code))
            break
        if('Content-Length'in r.headers):
            contentlen = int(r.headers['Content-Length'])
        
        #ERROR response may empty(facebook bug)
        if(contentlen==0):
            print('Response empty, Continue')

            if not os.path.isdir(ErrorPath):
                os.mkdir(ErrorPath)

            Err = open(ErrorPath + fbname+'-response.txt', 'wb')
            Err.write(r.content)
            
            break

        response = r.text

        #for json
        json_r = response.replace('for (;;);','')    
                        
        
        #creat json response
        json_r = json.loads(json_r)
        with open(dirPath + str(num)+'.json', 'w',encoding="utf-8") as json_file:
            json.dump(json_r,json_file,ensure_ascii=False)
            num=num+1
                    
        #cursor to payload
        try:        
            cursor = re.search(r'cursor=(.*?)&amp;surface', response.encode().decode('unicode-escape')).group(1)
            cursor = urllib.parse.unquote(cursor)
            payload['cursor'] = cursor
            
        except:
            print('Last Post')
            break
        

        #check date
        date = re.findall(r'data-utime=\\\"(\d+.*?)\\\"', response)
        try:
            date = int(date[-1])
            date = datetime.datetime.fromtimestamp(date-timezone).year
            if(date<=setyear):
                print('Post date <= Set year')
                break
        except:
            print('Time value emyty')
            break