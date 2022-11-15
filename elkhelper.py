import datetime
from dateutil.parser import parse
import requests
import pytz
import json

class elkhelper():
    '''
    elk操作类
    整体不做异常处理,请在使用时单独处理


    20220509研究根据条件更新数据
    get sh-market-seo/_search
    {
    "query":{
        "bool":{
        "must_not":{
            "exists":{
            "field":"排名"
            }
        }
        }  
    }
    }


    post sh-market-seo/_update_by_query
    {   
    "script": {
            "source": "ctx._source['排名']=999"
        },
    "query":{
        "match":{
        "_id":"IJngTH4BwNWUzoUlgfZc"
        }  
    }
    
    }


    '''

    def initialworkdays(self):
        workdays = self.searchAll('workday/_search?size=2000&q=workday:true')
        workdays = list( datetime.datetime.strptime(x['date'],'%Y%m%d').date() for x in workdays)
        workrange=[]
        for workday in workdays:
            wd = str(workday)
            wd = parse(wd)
            workrange.append(
                {
                    'date':str(workday)
                    ,'start':wd+datetime.timedelta(hours=9)
                    ,'end':wd+datetime.timedelta(hours=12)
                }
            )
            workrange.append(
                {
                    'date':str(workday)
                    ,'start':wd+datetime.timedelta(hours=13)
                    ,'end':wd+datetime.timedelta(hours=17.5)
                }
            )
        self.workdays=workdays
        self.workrange=workrange

    def __init__(self,host,auth):
        '''
        auth:账号信息，格式： ('username':'password')
        '''
        self.host=host
        self.auth=auth
        self.headers= {'Content-Type': 'application/json'}




    def getworkhours(self,start,end):
        start =start.replace(tzinfo=pytz.timezone('UTC'))   
        end= end.replace(tzinfo=pytz.timezone('UTC'))   
        workdays=self.workdays
        #简易的时间合规函数,碰到时区不同只能处理utc时间和北京时间
        def reguladate(dt):
            if dt.tzname() == 'UTC':
                timestr=datetime.datetime.strftime(dt,'%Y-%m-%dT%H:%M:%S+00:00')
            else:
                timestr=datetime.datetime.strftime(dt,'%Y-%m-%dT%H:%M:%S+08:00')
            dt = parse(timestr).replace(tzinfo=pytz.timezone('UTC'))
            return dt
        #核心算法,计算同一天内的工作小时数
        def getcdhours(start,end):   
            final = 0.0
            tday = list(filter(lambda x:x['date']==str(start.date()),self.workrange))
            if not tday==[]: 
                '''核心算法,实际上是取两条线段相交的部分'''   
                for i in tday:
                    ts=reguladate(i['start'])
                    te=reguladate(i['end'])
                    a1=start<ts
                    a2=start>=ts and start <= te
                    a3=start>te #开始时间大于范围结束,不用考虑
                    b1= end<ts  #结束时间大于范围开始,不用考虑
                    b2=end>=ts and end <=te
                    b3= end>te
                    if a3 or b1:
                        continue
                    if a1 and b2:
                        th= (end-ts).total_seconds()
                    if a1 and b3:
                        th=  (te-ts).total_seconds()
                    if a2 and b2:
                        th=  (end-start).total_seconds()
                    if a2 and b3:
                        th=  (te-start).total_seconds()   
                    final+=th
            return final/3600
        #时间合规
        start = reguladate(start)
        end = reguladate(end)
        totalhours=0.0
        #在当天就直接出结果
        if start.date()==end.date():      
            if start.date() in workdays:  
                return getcdhours(start,end)
        else:
            '''
            开始和结束不在同一天：
            1.首先计算第一天的工作小时数，把开始时间赋值给临时变量后自增一天   
            2.while循环:判断临时变量和结束日期是否在同一天，不在就直接加7.5个小时，得判断是不是工作日,然后再自增一天
            3.等到在同一天了，把时间改为9点，再使用临时变量和结束时间进行计算
            '''
            tmp=datetime.datetime(start.year,start.month,start.day,17,30)
            tmp=reguladate(tmp)
            totalhours+=getcdhours(start,tmp)
            tmp=start+datetime.timedelta(days=1)
            '''如果临时日期仍然小于结束日期，且属于工作日，则直接加7.5工作小时'''  
            while(tmp.date()<end.date()):          
                if tmp.date() in workdays:
                    totalhours+=7.5
                tmp+=datetime.timedelta(days=1)   
            tmp=datetime.datetime(tmp.year,tmp.month,tmp.day,9,0).replace(tzinfo=pytz.timezone('UTC'))   
            tmp=reguladate(tmp) 
            totalhours+=getcdhours(tmp,end)
        return totalhours

    def deleteidx(self,index):
        url = '{}/{}'.format(self.host,index)
        req = requests.delete(url,auth=self.auth)  
        print(json.loads(req.text))

    
    def delete(self,index,id):
        url = '{}/{}/_doc/{}'.format(self.host,index,id)
        req = requests.delete(url,auth=self.auth)        
        return json.loads(req.text)
        #日期时间格式处理
    def Strfelktime(self,dt):
        '''
        将字符串格式的时间日期转换成elk能够识别的格式,含北京时区
        '''
        if type(dt)==datetime.date:
            timestr=datetime.date.strftime(dt,'%Y-%m-%dT%H:%M+08:00')
            return timestr
        if type(dt)==str:
            dt=parse(dt)        
        if dt.tzname() == 'UTC':
            timestr=datetime.datetime.strftime(dt,'%Y-%m-%dT%H:%M+00:00')
        else:
            timestr=datetime.datetime.strftime(dt,'%Y-%m-%dT%H:%M+08:00')
        return timestr
    def put(self,index,obj):
        '''
        录入elk的方法
        host=主机地址[含端口号]
        index=索引名称
        obj=要录入elk的字典对象,要求有'id'键值
        '''
        data = json.dumps(obj,ensure_ascii=True)
        url='{}/{}/_doc/{}'.format(self.host,index,obj['id'])        
        req=requests.put(url,auth=self.auth,headers=self.headers,data=data.encode())
        result = json.loads(req.text)
        return result

        
    def bulk(self,index,dl):
        reqtext=''
        for obj in dl:
            o1={ "index" : { "_index" : index, "_id" :obj['id'] } }
            o2=obj
            d1 = json.dumps(o1,ensure_ascii=False)
            d2=json.dumps(o2,ensure_ascii=False)
            d3=d1+'\n'+d2+'\n'
            reqtext+=d3
        ss=requests.post(self.host+'/_bulk',auth=self.auth,headers=self.headers,data=reqtext.encode())
        return json.loads(ss.text)
    def putDictList(self,index,dl):
        '''字典列表直接入elk
        自动将日期时间转换为elk时间
        同样每个字典需要id字段
        '''
        for d in dl:
            for f in d:
                if type(d[f])==datetime.datetime:
                    d[f]=self.Strfelktime(d[f])
                if type(d[f])==datetime.date:
                    d[f]=str(d[f])
            self.put(index,d)
    
    def getdoc(self,index,id):
        url = '{}/{}/_doc/{}'.format(self.host,index,id)
        req = requests.get(url,auth=self.auth)
        res = json.loads(req.text)
        return res

    
    
    def searchdoc(self,querystr):
        '''
        单页查询,最大支持10000条数据
        querystr直接写索引名加搜索字符串,如下
        index/_search?size=xxxx?q=xxxx:xxx                        
        '''
        url = '{}/{}'.format(self.host,querystr)
        req = requests.get(url,auth=self.auth)
        res =json.loads(req.text)
        if not 'error' in res:
            result = list(x for x in res['hits']['hits'])
            return result
        else:
            return []
    
    def get_es_stamp(self):
        return datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%dT%H:%M+08:00')





    def search(self,querystr):
        '''
        单页查询,最大支持10000条数据
        querystr直接写索引名加搜索字符串,如下
        index/_search?size=xxxx?q=xxxx:xxx                        
        '''
        url = '{}/{}'.format(self.host,querystr)
        req = requests.get(url,auth=self.auth)
        res =json.loads(req.text)
        if not 'error' in res:
            result = list(x['_source'] for x in res['hits']['hits'])
            return result
        else:
            return []
    
    def query(self,index,field,str,size=8000):
        body={
        "query":{
            "wildcard":{field+".keyword": {"value":"*{}*".format(str)}}
        }
        }
        url = '{}/{}/_search?size={}'.format(self.host,index,size)
        data = json.dumps(body,ensure_ascii=True)
        res = requests.post(url,headers=self.headers,auth=self.auth,data=data.encode())
        result = json.loads(res.text)
        data = result['hits']['hits']
        return data


    def deletebyquery(self,index,field,str):
        body={
            "query":{
                "wildcard":{field+".keyword": {"value":"*{}*".format(str)}}
            }
        }
        url = '{}/{}/_delete_by_query'.format(self.host,index)
        data = json.dumps(body,ensure_ascii=True)
        res = requests.post(url,headers=self.headers,auth=self.auth,data=data.encode())
        result = json.loads(res.text)
        return result


    def Tsearch(self,idx,body):
        '''
        全量数据查询,当所需要的数据量大于10000条时使用，使用post方法发送请求体进行精确查询
        body的构建方法
        body= {
            "query": {
                "bool": {
                "must": [
                    {
                    "range": {
                        "timestamp": {
                        "gte": "2022-01-09",
                        "lt": "2022-05-10"
                        }
                    }
                    }
                ]
                }
            }
            }
        '''
        url = f"{self.host}/{idx}/_search?size=9999&scroll=1m"
        data = json.dumps(body,ensure_ascii=False)
        res = requests.post(url,headers=self.headers,auth=self.auth,data=data.encode())
        result =json.loads(res.text)

        if 'hits' in result:
            data = list(x['_source'] for x in result['hits']['hits'])
        else:
            return []
        sid = result['_scroll_id']
        total = result['hits']['total']['value']
        while len(data)<total:        
            print('翻页')
            url='{}/_search/scroll?scroll_id={}&scroll=1m'.format(self.host,sid)
            req=requests.get(url,auth=self.auth)
            result=json.loads(req.text)
            data+=list(x['_source'] for x in result['hits']['hits'])
        return data
    def getAllData(self,idx):
        # url = '{}/{}&scroll=1m'.format(self.host,querystr)
        querystr = f"{idx}/_search?size=5000"
        # data = self.searchAll(querystr)
        return self.searchAll(querystr)
    def searchAll(self,querystr):
        '''
        全量数据查询,当所需要的数据量大于10000条时使用
        querystr直接写索引名加搜索字符串,如下
        index/_search?size=xxxx?q=xxxx:xxx   
        '''
        url = '{}/{}&scroll=1m'.format(self.host,querystr)
        req = requests.get(url,auth=self.auth)
        result =json.loads(req.text)
        if 'hits' in result:
            data = list(x['_source'] for x in result['hits']['hits'])
        else:
            return []

        sid = result['_scroll_id']
        total = result['hits']['total']['value']
        while len(data)<total:
            url='{}/_search/scroll?scroll_id={}&scroll=1m'.format(self.host,sid)
            req=requests.get(url,auth=self.auth)
            result=json.loads(req.text)
            data+=list(x['_source'] for x in result['hits']['hits'])
        return data

    def bulkbypage(self,data,limit):
        page = int(len(data)/limit)
        if len(data)%limit !=0:
            page+=1
        for i in range(0,page):
            req = data[i*limit:][:limit]
            res = json.loads(self.bulk('sh-crm-incomes',req))
            print(res['errors'])

class workday():
    def __init__(self):
        self.url="http://10.10.10.108:9200/"        
        elk =elkhelper(self.url,('user','123456'))
        workdays = elk.searchAll("workday/_search?size=9999")
        self.workdaylist = workdays
        workdays = list(filter(lambda x:x['workday'],workdays))
        workdays = list( datetime.datetime.strptime(x['date'],'%Y%m%d').date() for x in workdays)
        workrange=[]
        for workday in workdays:
            wd = str(workday)
            wd = parse(wd)
            workrange.append(
                {
                    'date':str(workday)
                    ,'start':wd+datetime.timedelta(hours=9)
                    ,'end':wd+datetime.timedelta(hours=12)
                }
            )
            workrange.append(
                {
                    'date':str(workday)
                    ,'start':wd+datetime.timedelta(hours=13)
                    ,'end':wd+datetime.timedelta(hours=17.5)
                }
            )
        self.fworkdays=workdays
        self.workrange=workrange



    def getnextworkday(self,currentday):
        nd = currentday+datetime.timedelta(days=1)
        while not self.ifwork(nd):
            nd+=datetime.timedelta(days=1)
        return nd
    
    def getworkdays(self,start:datetime,end:datetime):        
        #计算消费了几个工作日，精确到天
        checkdays=[]
        fd=True
        while start.date() <=end.date() :        
            if fd:
                fd=False
            else:
                startday = start.strftime('%Y%m%d')
                checkdays.append(startday)
            start+=datetime.timedelta(days=1) 
        workdayscount = list(filter(lambda x:x['date'] in checkdays and x['workday'],self.workdaylist))
        return len(workdayscount)
    def xiuxi(self,today):
        headers = {'Content-Type': 'application/json'}
        elkdays = self.url+'workday/workday/_search?size=5000'
        workdays = requests.get(elkdays,auth=('user','123456'),headers=headers)
        workdays = json.loads(workdays.text)['hits']['hits']
        workdaylist = list(x['_source'] for x in workdays)
        return today in workdaylist
        
    def getspecialday(self,start,days):
        targetday = start
        while not (self.getworkdays(start,targetday)==days):
            targetday+=datetime.timedelta(days=1)    
        return targetday


    def ifwork(self,currentday):
        wdl = {x['date']:x for x in self.workdaylist}
        if currentday.strftime('%Y%m%d') in wdl:
            target = wdl[currentday.strftime('%Y%m%d')]
            return target['workday']
        return False

    def getworkhours(self,start,end):
        start =start.replace(tzinfo=pytz.timezone('UTC'))   
        end= end.replace(tzinfo=pytz.timezone('UTC'))   
        workdays=self.fworkdays
        #简易的时间合规函数,碰到时区不同只能处理utc时间和北京时间
        def reguladate(dt):
            if dt.tzname() == 'UTC':
                timestr=datetime.datetime.strftime(dt,'%Y-%m-%dT%H:%M:%S+00:00')
            else:
                timestr=datetime.datetime.strftime(dt,'%Y-%m-%dT%H:%M:%S+08:00')
            dt = parse(timestr).replace(tzinfo=pytz.timezone('UTC'))
            return dt
        #核心算法,计算同一天内的工作小时数
        def getcdhours(start,end):   
            final = 0.0
            tday = list(filter(lambda x:x['date']==str(start.date()),self.workrange))
            if not tday==[]: 
                '''核心算法,实际上是取两条线段相交的部分'''   
                for i in tday:
                    ts=reguladate(i['start'])
                    te=reguladate(i['end'])
                    a1=start<ts
                    a2=start>=ts and start <= te
                    a3=start>te #开始时间大于范围结束,不用考虑
                    b1= end<ts  #结束时间大于范围开始,不用考虑
                    b2=end>=ts and end <=te
                    b3= end>te
                    if a3 or b1:
                        continue
                    if a1 and b2:
                        th= (end-ts).total_seconds()
                    if a1 and b3:
                        th=  (te-ts).total_seconds()
                    if a2 and b2:
                        th=  (end-start).total_seconds()
                    if a2 and b3:
                        th=  (te-start).total_seconds()   
                    final+=th
            return round(final/3600,2)
        #时间合规
        start = reguladate(start)
        end = reguladate(end)
        totalhours=0.0
        #在当天就直接出结果
        if start.date()==end.date():      
            if start.date() in workdays:  
                return round(getcdhours(start,end),2)
            else:
                return 0.0
        else:
            '''
            开始和结束不在同一天：
            1.首先计算第一天的工作小时数，把开始时间赋值给临时变量后自增一天   
            2.while循环:判断临时变量和结束日期是否在同一天，不在就直接加7.5个小时，得判断是不是工作日,然后再自增一天
            3.等到在同一天了，把时间改为9点，再使用临时变量和结束时间进行计算
            '''
            tmp=datetime.datetime(start.year,start.month,start.day,17,30)
            tmp=reguladate(tmp)
            totalhours+=getcdhours(start,tmp)
            tmp=start+datetime.timedelta(days=1)
            '''如果临时日期仍然小于结束日期，且属于工作日，则直接加7.5工作小时'''  
            while(tmp.date()<end.date()):          
                if tmp.date() in workdays:
                    totalhours+=7.5
                tmp+=datetime.timedelta(days=1)   
            tmp=datetime.datetime(tmp.year,tmp.month,tmp.day,9,0).replace(tzinfo=pytz.timezone('UTC'))   
            tmp=reguladate(tmp) 
            totalhours+=getcdhours(tmp,end)
        return round(totalhours,2)

