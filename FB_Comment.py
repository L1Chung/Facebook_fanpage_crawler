import requests 
import urllib
import os
import re
import json
import datetime
import pandas
import time
from bs4 import BeautifulSoup 

#IMPORTANT
################################################
url = 'https://www.facebook.com/api/graphql/'

headers = {
    'user-agent': 'Chrome/81.0.4044.138' 
}

cookies = {#put cookie may solve some problem when crawling
    'cookie': ''
}
################################################

with open('./CrawList.txt',encoding='utf-8') as page_file:
    pageList = (line.rstrip() for line in page_file) 
    pageList = list(line for line in pageList if line)

dirPath = './Comment/'
if not os.path.isdir(dirPath):
    os.mkdir(dirPath)

for name in pageList:

    print(name)
    #Read file
    path = './Analysize/'+name+'.pkl'
    pkl = pandas.read_pickle(path)
    comment = pkl['Total Comment']
    feedid = pkl['FeedbackID']

    #Creat Path
    dirPath = './Comment/'+name
    if not os.path.isdir(dirPath):
        os.mkdir(dirPath)

    for i in range(len(comment)):
        #Set Params
        feedbackID = ''
        cursor = 'null'

        if((comment[i]>0) & (feedid[i]!='')):
            count = 0
            feedbackID = feedid[i]

            dirPath = './Comment/'+name+'/'+feedbackID+'/'

            #Check previous
            if os.path.isdir(dirPath):

                if os.listdir(dirPath):

                    fname = os.listdir(dirPath)
                    fname.sort(key=lambda f: int(re.sub('\D','', f)))
                    fname = fname[-1]
                    fcheck = open(dirPath+fname,'r',encoding='utf-8').read()
                    fcheck = json.loads(fcheck)
                    #In case post has been deleted
                    try:
                        page_info = fcheck['data']['feedback']['display_comments']['page_info']
                        next_page = page_info['has_next_page']
                    except:
                        continue

                    if(next_page!=False):
                        cursor = '\"'+page_info['end_cursor']+'\"'
                        count = int(fname.replace('.json',''))+1
                    else:
                        continue        
            else:
                os.mkdir(dirPath)

            payload = {
            'av': '0',
            '__user': '0',
            '__a': '1',
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'UFI2CommentsProviderPaginationQuery',
            'variables': '{"after":'+cursor+',"before":null,"displayCommentsFeedbackContext":"{\\"bump_reason\\":0,\\"comment_expand_mode\\":1,\\"comment_permalink_args\\":{\\"comment_id\\":null,\\"reply_comment_id\\":null,\\"filter_non_supporters\\":null},\\"interesting_comment_fbids\\":[],\\"is_location_from_search\\":false,\\"last_seen_time\\":null,\\"log_ranked_comment_impressions\\":true,\\"probability_to_comment\\":0,\\"story_location\\":4,\\"story_type\\":0}","displayCommentsContextEnableComment":false,"displayCommentsContextIsAdPreview":false,"displayCommentsContextIsAggregatedShare":false,"displayCommentsContextIsStorySet":false,"feedLocation":"PAGE_TIMELINE","feedbackID":\"'+feedbackID+'\","feedbackSource":22,"first":50,"focusCommentID":null,"includeNestedComments":true,"isInitialFetch":false,"isComet":false,"containerIsFeedStory":true,"containerIsWorkplace":false,"containerIsLiveStory":false,"containerIsTahoe":false,"last":null,"scale":1.5,"topLevelViewOption":null,"useDefaultActor":true,"viewOption":"RANKED_UNFILTERED","UFI2CommentsProvider_commentsKey":null}',
            'doc_id': '3408461259184070'
            }

            while True:

                r = requests.post(url,headers = headers,params= payload,cookies = cookies)
                #Sometimes cant load more comment(facebook bug?)
                if(r.status_code!=200):
                    break

                response = r.text

                json_r = json.loads(response)
                
                with open(dirPath+str(count)+'.json', 'w',encoding="utf-8") as json_file:
                    json.dump(json_r,json_file,ensure_ascii=False)
                    count+=1

                #In case post has been deleted
                try:
                    page_info = json_r['data']['feedback']['display_comments']['page_info']
                    next_page = page_info['has_next_page']
                except:
                    break

                if(next_page!=True):
                    break

                cursor = '\"'+page_info['end_cursor']+'\"'
                payload = {
                    'av': '0',
                    '__user': '0',
                    '__a': '1',
                    'fb_api_caller_class': 'RelayModern',
                    'fb_api_req_friendly_name': 'UFI2CommentsProviderPaginationQuery',
                    'variables': '{"after":'+cursor+',"before":null,"displayCommentsFeedbackContext":"{\\"bump_reason\\":0,\\"comment_expand_mode\\":1,\\"comment_permalink_args\\":{\\"comment_id\\":null,\\"reply_comment_id\\":null,\\"filter_non_supporters\\":null},\\"interesting_comment_fbids\\":[],\\"is_location_from_search\\":false,\\"last_seen_time\\":null,\\"log_ranked_comment_impressions\\":true,\\"probability_to_comment\\":0,\\"story_location\\":4,\\"story_type\\":0}","displayCommentsContextEnableComment":false,"displayCommentsContextIsAdPreview":false,"displayCommentsContextIsAggregatedShare":false,"displayCommentsContextIsStorySet":false,"feedLocation":"PAGE_TIMELINE","feedbackID":\"'+feedbackID+'\","feedbackSource":22,"first":50,"focusCommentID":null,"includeNestedComments":true,"isInitialFetch":false,"isComet":false,"containerIsFeedStory":true,"containerIsWorkplace":false,"containerIsLiveStory":false,"containerIsTahoe":false,"last":null,"scale":1.5,"topLevelViewOption":null,"useDefaultActor":true,"viewOption":"RANKED_UNFILTERED","UFI2CommentsProvider_commentsKey":null}',
                    'doc_id': '3408461259184070'
                    }
