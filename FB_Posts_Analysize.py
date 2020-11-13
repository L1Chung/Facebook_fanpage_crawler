import requests 
import urllib
import os
import re
import json
import datetime
import pandas
from bs4 import BeautifulSoup 

#Facebook time
timezone = 54000 #Taiwan timezone
dirPath = './json_Data/'
fbname = ''
savePath = './Analysize/'
if not os.path.isdir(savePath):
    os.mkdir(savePath)

with open('./CrawList.txt',encoding='utf-8') as page_file:
    pageList = (line.rstrip() for line in page_file) 
    pageList = list(line for line in pageList if line)

for fbname in pageList:

    print('Analysing-'+fbname)
    
    if os.path.isfile(savePath+fbname+'.pkl'):
        print(fbname + ' analysized.')
        continue
    
    List = {
    'Name':[],
    'Page ID':[],
    'Post ID':[],
    'Time':[],
    'Content':[],
    'Total Comment':[],
    'Display Comment':[],
    'Share count':[],
    'Reaction count':[],
    'LIKE':[],
    'LOVE':[],
    'HAHA':[],
    'WOW':[],
    'SORRY':[],
    'ANGER':[],
    'SUPPORT':[],
    'Quote':[],
    'Quote content':[],
    'Quote link':[],
    'Img link':[],
    'Img alt':[],
    'Img label':[],
    'Video content':[],
    'Video link':[],
    'FeedbackID':[]
    }
    
    result = os.listdir(dirPath+fbname)
    result.sort(key=lambda f: int(re.sub('\D','', f)))
    
    for count in result:
        
        with open(dirPath + fbname+'\\'+str(count), 'r',encoding="utf-8") as json_file:
                jsfile = json_file.read()
                html = json.loads(jsfile)
                html = str(html["domops"][0][3])
                
            
        
        soup = BeautifulSoup(html,'lxml')

        #Content info
        #############
        ContentInfo = soup.find_all('div','_5pcr userContentWrapper')
        #############

        for cinfo in ContentInfo:
            
            #Content
            try:
                #Text in image box(In case text duplicate)
                Content = cinfo.find('div',{'data-testid':'post_message'})
                Content = Content.find("span",{'class':'_5z6m'}).text
                List['Content'].append(str(Content))
            except:
                try:
                    #Content text
                    Content = cinfo.find('div',{'data-testid':'post_message'}).text
                    List['Content'].append(str(Content))
                except:
                    try:
                        #No content
                        Content = cinfo.find("div",'clearfix _2r3x').text
                        List['Content'].append('')
                    except:
                        try:
                            #Update status
                            Content = cinfo.find('div','_6a _5u5j _6b').text
                            List['Content'].append(str(Content))
                        except:
                            List['Content'].append('')

            List['Quote'].append('')
            List['Quote content'].append('')
            List['Quote link'].append('')
            List['Img link'].append('')
            List['Img alt'].append('')
            List['Img label'].append('')
            List['Video content'].append('')
            List['Video link'].append('')
            

            try:
                #Quote others post
                Quote = cinfo.find("div",'_5r69 _sds')
                try:
                    List['Quote'][-1] = Quote.find('div','plm _42ef').text
                except:
                    pass

                try:
                    List['Quote content'][-1] = Quote.find('div','mtm _5pcm').text
                except:
                    pass

                try:
                    List['Quote link'][-1] = Quote.find("a")['href']
                except:
                    pass
                
            except:
                pass
                

            try:
                #Quote link or img
                Quote = cinfo.find("div",'clearfix _2r3x')
                try:
                    List['Quote'][-1] = Quote.find("a")['aria-label']
                except:
                    pass

                try:
                    List['Quote link'][-1] = Quote.find("a")['href']
                except:
                    pass

                try:
                    List['Quote content'][-1] = Quote.text
                except:
                    pass
                    
                    
            except:
                pass

            #######
            try:
                #Get img info
                Img = cinfo.find_all("a",{'rel':'theater'})

                quote_Img = cinfo.find("img",'scaledImageFitWidth img')

                try:
                    if quote_Img['data-src'].find('safe_image.php')!=-1:
                        List['Img link'][-1] += quote_Img['data-src'] +'\n'
                except:
                    pass

                for imglink in Img:
                    
                    try:
                        List['Img link'][-1] += imglink['data-ploi'] + '\n'
                    except:
                        pass

                    try:
                        List['Img alt'][-1] += imglink['alt']+ '\n'
                    except:
                        pass

                    try:
                        List['Img label'][-1] += imglink['aria-label']+ '\n'
                    except:
                        pass
            except:
                pass

            ####
            try:
                #Get Video info
                Video = cinfo.find('div','_567v _3bw _4ubd _28dy _3htz')

                try:
                    List['Video content'][-1] = Video.text
                    List['Quote content'][-1] = ''
                except:
                    pass

                try:
                    List['Video link'][-1] = Video.find('a')['href']
                    List['Quote link'][-1] = ''
                except:
                    pass
            except:
                pass
            

        #poster info
        #############
        PosterInfo = soup.find_all('div','l_c3pyo2v0u _5eit i_c3pynyi2f clearfix')
        #############

        for pinfo in PosterInfo:

            #ID               
            ID = pinfo.find('div', {'class':'_5pcp _5lel _2jyu _232_'}).attrs['id'].split(';')[0].split('_')[-1]
            List['Page ID'].append(ID)

            #Name
            Name = pinfo.find('img').attrs['aria-label']
            List['Name'].append(Name)
            
            #Time
            Time = pinfo.find('abbr').attrs['data-utime']
            Time = datetime.datetime.fromtimestamp(int(Time)-timezone)
            List['Time'].append(Time)

            
        #############
        #Comment info
        #############
        CommentInfo = soup.find_all('form',{'class':'commentable_item'})
        for cminfo in CommentInfo:
            cminfo = cminfo.find('input',{'name':'ft_ent_identifier'})
            PostID = cminfo.attrs['value']
            List['Post ID'].append(PostID)
            List['LIKE'].append(0)
            List['LOVE'].append(0)
            List['HAHA'].append(0)
            List['WOW'].append(0)
            List['SORRY'].append(0)
            List['ANGER'].append(0)
            List['SUPPORT'].append(0)
            List['Reaction count'].append(0)
            List['Total Comment'].append(0)
            List['Display Comment'].append(0) 
            List['Share count'].append(0)
            List['FeedbackID'].append('')

            feedback = re.findall(r'\"feedback\": (.*?]})}', jsfile)
            #Get feedback id
            for FeedID in feedback:
                
                search = FeedID.find(PostID)
                #Post's feedback id in json is not sorted
                if(search!=-1):
                    
                    FeedID = json.loads(FeedID)
                    
                    List['FeedbackID'][-1]=(FeedID['id'])
                    List['Reaction count'][-1]=(FeedID['reaction_count']['count'])
                    List['Total Comment'][-1]=(FeedID['comment_count']['total_count'])
                    List['Display Comment'][-1]=(FeedID['display_comments_count']['count']) 
                    List['Share count'][-1]=(FeedID['share_count']['count'])
                        

                    for reactnum in range(len(FeedID['top_reactions']['edges'])):
                        #Count different reaction
                        reactList = FeedID['top_reactions']['edges'][reactnum]
                        reaction_count = reactList.get('reaction_count')
                        react_type = reactList.get('node').get('reaction_type')
                        List[react_type][-1] = reaction_count

            #Live video
            live = re.findall(r'"feedbacktarget": ({.*?}]})}', jsfile)
            for liveID in live:
                search = liveID.find(PostID)
                if(search!=-1):

                    liveID = json.loads(liveID)
                    List['Total Comment'][-1]=(liveID['commentcount'])
                    List['Display Comment'][-1]=(liveID['commentcount']) 
                    List['Reaction count'][-1]=(liveID['likecount'])
                    List['LIKE'][-1]=(liveID['likecount'])
                    List['Share count'][-1]=(liveID['sharecount'])
                        
    
    
    pickle = pandas.DataFrame(List)
    pickle.to_pickle(savePath+fbname+'.pkl')
    pickle.to_csv(savePath+fbname+'.csv',encoding="utf-8-sig")
    print(fbname + ' analysized.')