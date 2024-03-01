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


    def __init__(self,host,auth):
        '''
        auth:账号信息，格式： ('username':'password')
        '''
        self.host=host
        self.auth=auth
        self.headers= {'Content-Type': 'application/json'}




    def deleteidx(self,index):
        url = '{}/{}'.format(self.host,index)
        req = requests.delete(url,auth=self.auth,verify=False)  
        print(json.loads(req.text))

    
    def delete(self,index,id):
        url = '{}/{}/_doc/{}'.format(self.host,index,id)
        req = requests.delete(url,auth=self.auth,verify=False)        
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
        req=requests.put(url,auth=self.auth,headers=self.headers,data=data.encode(),verify=False)
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
        ss=requests.post(self.host+'/_bulk',auth=self.auth,headers=self.headers,data=reqtext.encode(),verify=False)
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
        req = requests.get(url,auth=self.auth,verify=False)
        res = json.loads(req.text)
        return res

    
    
    def searchdoc(self,querystr):
        '''
        单页查询,最大支持10000条数据
        querystr直接写索引名加搜索字符串,如下
        index/_search?size=xxxx?q=xxxx:xxx                        
        '''
        url = '{}/{}'.format(self.host,querystr)
        req = requests.get(url,auth=self.auth,verify=False)
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
        req = requests.get(url,auth=self.auth,verify=False)
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
        res = requests.post(url,headers=self.headers,auth=self.auth,data=data.encode(),verify=False)
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
        res = requests.post(url,headers=self.headers,auth=self.auth,data=data.encode(),verify=False)
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
        res = requests.post(url,headers=self.headers,auth=self.auth,data=data.encode(),verify=False)
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
            req=requests.get(url,auth=self.auth,verify=False)
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
        req = requests.get(url,auth=self.auth,verify=False)
        result =json.loads(req.text)
        if 'hits' in result:
            data = list(x['_source'] for x in result['hits']['hits'])
        else:
            return []

        sid = result['_scroll_id']
        total = result['hits']['total']['value']
        while len(data)<total:
            url='{}/_search/scroll?scroll_id={}&scroll=1m'.format(self.host,sid)
            req=requests.get(url,auth=self.auth,verify=False)
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
