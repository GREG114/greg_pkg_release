import json
import requests
class YiDaHelper:
    @staticmethod
    
    def byPage(dataList,size,fun):
        pages = len(dataList)/size
        if pages%1!=0:
            pages = int(pages)+1
        else:
            pages=int(pages)
        for i in range(0,pages):
            list_s=i+size
            list_e=list_s+size
            sub = dataList[list_s:list_e]
            fun(sub)

    @staticmethod
    def getdpusers(token,dpid,offset=0,size=100):
        userurl = 'https://oapi.dingtalk.com/user/listbypage?access_token={}&department_id={}&offset={}&size={}'.format(token,dpid,offset,size)
        result = requests.get(userurl)
        users = json.loads(result.text)
        return users
    @staticmethod
    def getuserinfo(userid,token):
        userurl='https://oapi.dingtalk.com/user/get?access_token={}&userid={}'.format(token,userid)    
        result = requests.get(userurl)
        user = json.loads(result.text)
        return user 

    @staticmethod
    def getDepartments(token,id=1):
        url = 'https://oapi.dingtalk.com/department/list?access_token={}&id={}&fetch_child=True'.format(token,id)
        request = requests.get(url)
        result = json.loads(request.text)
        return result
    #构造函数，userid没有的话宜搭后面的不好操作，但是初始化时不知道可以不填，之后获取好记得写过来就可以
    def __init__(self,appkey,appsecret,appType,systemToken,userid=""):
        self.host = 'https://oapi.dingtalk.com'
        self.headers={'Content-Type': 'application/json'}
        self.userid=userid
        self.appType=appType
        self.systemToken=systemToken
        url = self.host+'/gettoken?appsecret={}&appkey={}'.format(appsecret,appkey)
        result = requests.get(url)
        result = json.loads(result.text)
        self.token = result['access_token']
        self.headers['x-acs-dingtalk-access-token']=self.token
    
    def batchUpdate(self,formUuid:str,formInstanceIdList:list
    ,updateFormDataJson:str,noExecuteExpression=False,ignoreEmpty=True,
    useLatestFormSchemaVersion=True,asynchronousExecution=True):
        req={
        "noExecuteExpression" : noExecuteExpression,
        "formUuid" : formUuid,
        "updateFormDataJson" : updateFormDataJson,
        "appType" : self.appType,
        "ignoreEmpty" : ignoreEmpty,
        "systemToken" :  self.systemToken,
        "useLatestFormSchemaVersion" : useLatestFormSchemaVersion,
        "asynchronousExecution" : asynchronousExecution,
        "formInstanceIdList" : formInstanceIdList,
        "userId" : self.userid,
        }
        data = json.dumps(req)
        url=f'https://api.dingtalk.com/v1.0/yida/forms/instances/components'
        result = requests.put(url,headers=self.headers,data=data.encode())
        if result.status_code in [200,201,202]:
            result = json.loads(result.text)
            return result
        else:
            raise Exception(f"数据更新异常:{result}")

    def batchRemove(self,formUuid:str,formInstanceIdList:list,asynchronousExecution=True):
        req={
        "appType" : self.appType,
        "systemToken" : self.systemToken,
        "userId" : self.userid,
        "formUuid" : formUuid,
        "formInstanceIdList":formInstanceIdList,
        "asynchronousExecution":asynchronousExecution
        }
        data = json.dumps(req)
        url=f'https://api.dingtalk.com/v1.0/yida/forms/instances/batchRemove'
        result = requests.post(url,headers=self.headers,data=data.encode())        
        if result.status_code in [200,201,202]:
            result = json.loads(result.text)
            return result
        else:
            raise Exception(f"数据更新异常:{result}")

    def formInfo(self,formUuid:str):
        url=f'https://api.dingtalk.com/v1.0/yida/forms/definitions/{self.appType}/{formUuid}?systemToken={self.systemToken}&userId={self.userid}'
        result = requests.get(url,headers=self.headers)
        result = json.loads(result.text)
        return result
    
    def processStart(self,processCode:str,formUuid:str,formDataJson:str):
        req={
            "appType" : self.appType,
            "systemToken" : self.systemToken,
            "userId" : self.userid,
            "formUuid" : formUuid,
            "formDataJson" : formDataJson,
            "processCode" : processCode,
        }
        data = json.dumps(req)
        url=f'https://api.dingtalk.com/v1.0/yida/processes/instances/start'
        result = requests.post(url,headers=self.headers,data=data.encode())        
        if result.status_code in [200,201,202]:
            result = json.loads(result.text)
            return result
        else:
            raise Exception(f"数据更新异常:{result}")

    def formSearch(self,formUuid:str,searchFieldJson:str,currentPage=1):
        req={
            "appType" : self.appType,
            "systemToken" : self.systemToken,
            "userId" : self.userid,
            "formUuid" : formUuid,
            "searchFieldJson" : searchFieldJson,
            "pageSize" : 100,
            "currentPage":currentPage
        }
        data = json.dumps(req)
        url=f'https://api.dingtalk.com/v1.0/yida/forms/instances/search'
        result = requests.post(url,headers=self.headers,data=data.encode())  
        if result.status_code in [200,201,202]:
            result = json.loads(result.text)
            return result
        else:
            raise Exception(f"数据更新异常:{result}")
    
    def getAllData(self,uuid:str,searchFieldJson:str):
        result =[]    
        cp=1
        res_targets = self.formSearch(uuid,searchFieldJson)
        result+= res_targets['data']
        while(len(result)< res_targets['totalCount']):
            cp+=1
            res_targets = self.formSearch(uuid,searchFieldJson,currentPage=cp)
            result+= res_targets['data']
        return result    
    
    def batchSave(self,formUuid:str,formDataJsonList:list,
    noExecuteExpression=False,keepRunningAfterException=False,asynchronousExecution=False):
        '''
        noExecuteExpression:是否不触发表单绑定的校验规则、关联业务规则和第三方服务回调。true：不触发
        asynchronousExecution:是否需要宜搭服务端异步执行该任务。true：允许。
        keepRunningAfterException:批量保存多条表单实例数据发生异常时是否跳过异常的表单实例并继续保存下一个表单实例数据。true：跳过
        '''
        req={
        "noExecuteExpression" : noExecuteExpression,
        "keepRunningAfterException":keepRunningAfterException,
        "asynchronousExecution":asynchronousExecution,
        "appType" : self.appType,
        "systemToken" : self.systemToken,
        "userId" : self.userid,
        "formUuid" : formUuid,
        "formDataJsonList" : formDataJsonList,
        }
        data = json.dumps(req)
        url=f'https://api.dingtalk.com/v1.0/yida/forms/instances/batchSave'
        result = requests.post(url,headers=self.headers,data=data.encode())
        result = json.loads(result.text)
        return result