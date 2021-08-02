
import requests
import json
from dateutil.parser import parse

class JiraOP():
    def __init__(self,host,auth):
        '''
        host:jira地址，如：http://service.i-search.com.cn
        auth:账号信息，格式如：{"username":"username","password":"password"}
        '''
        self.headers={'Content-Type': 'application/json'}
        self.host=host
        self.auth=auth
        self.login()


    def getspecialconsumed(self,keywords,logs):
        '''
        查找jira工单里特定状态的耗时
        logs为工单的改动记录，时间戳是顺序的，也可以再来一次排序
        '''    
        sconsumed=None
        logs = sorted(logs,key=lambda x:parse(x['created']))
        def check(x,key):
            #判断该事件是否追踪
            events = list(filter(lambda y:y['toString']==key or y['fromString']==key,x['items']))
            return len(events)>0
        def is_in(x,key):
            events = list(filter(lambda y:y['toString']==key,x['items']))
            return len(events)>0

        for key in keywords:
            keylogs = list(filter(lambda x:check(x,key),logs))     
            keystart=None
            if len(keylogs)>0:       
                for keylog in keylogs:
                    if is_in(keylog,key):
                        keystart=parse(keylog['created'])
                    else:
                        delta = parse(keylog['created'])-keystart
                        if sconsumed==None:
                            sconsumed=delta
                        else:
                            sconsumed+=delta
                #计算进入该状态消耗的时间    
        return sconsumed

    def login(self):
        url=self.host+'/rest/auth/1/session'
        data=json.dumps(self.auth,ensure_ascii=True)
        result =requests.post(url,headers=self.headers,data=data.encode())
        result=json.loads(result.text)
        session=result['session']
        sessionStr= session['name']+'='+session['value']
        self.headers.update({'cookie':sessionStr})

    def getissuedetail(self,key):
        logurl=self.host+'/rest/api/2/issue/{}'.format(key)
        req = requests.request('GET',logurl,headers=self.headers)
        res = json.loads(req.text)
        return res

    def getissues(self,jql):
        issue = self.host+'/rest/api/2/search'
        result = requests.request('GET',issue,headers=self.headers,params=jql)
        res = json.loads(result.text)
        result=res['issues']
        total=res['total']
        count=len(result)        
        while(count<total):
            jql['startAt']=count
            res = requests.request('GET',issue,headers=self.headers,params=jql)
            res = json.loads(res.text)
            result+=res['issues']
            count=len(result)
        return result

    def getLog(self,key):
        query={
        'maxResults':1000
        }
        logurl = self.host+'/rest/api/2/issue/{}?expand=changelog&fields=summary&maxResults=20'.format(key)
        result = requests.request("GET",logurl,headers=self.headers,params=query)
        result =json.loads(result.text)
        changelog = result["changelog"]["histories"]
        return changelog

