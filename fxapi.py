import requests
import json
import time
import random
from dateutil.parser import parse
class fxapi():
    headers = {'content-Type':'application/json'}
    appsecret_crm=''
    appid=''
    #替换成自己的吧，我这个沙盒里的你拿去也没用，放着我自己用的方便
    currentuserid='FSUID_8C93C81AC05591B4941ADCEABC5F92B0'
    token=''
    corpid=''
    permanentCode=''
    headers = {'content-Type':'application/json'}
    host='https://open.fxiaoke.com'


    def __init__(self,appid,appsecret_crm,permanentCode):
        self.appid=appid
        self.appsecret_crm=appsecret_crm
        self.permanentCode=permanentCode
        
        #正式系统        
        req={
            'appId':self.appid
            ,'appSecret':self.appsecret_crm
            ,'permanentCode':self.permanentCode
        }
        
        url = f'{self.host}/cgi/corpAccessToken/get/V2'
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        obj_res = json.loads(res.text)
        self.token=obj_res['corpAccessToken']
        self.corpid=obj_res['corpId']
        
    @staticmethod
    def randomnames(args, numbers):
        result = []
        while len(result) < numbers:
            cpname = ''
            for i in args:
                name = random.sample(args[i], 1)[0]
                cpname += str(name)
            if not cpname in result:
                result.append(cpname)
                print(cpname)
        return result


    def get_process_approval_list(self,dataid):
        req={
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "dataId":dataid
        } 
        url = '{}/cgi/crm/object/approvalInstances/query'.format(self.host)
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return json.loads(res.text)

    def get_approvalinstance(self,instanceid):
        req={
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "instanceId":instanceid
        } 
        url = '{}/cgi/crm/approvalInstance/get'.format(self.host)
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return json.loads(res.text)

    def approvalTaskAction(self,taskId,actionType,opinion):
        req={
        "corpAccessToken": self.token,
        "corpId": self.corpid,
        "currentOpenUserId": self.currentuserid,
        "actionType":actionType,
        "opinion":opinion,
        "taskId":taskId,
        } 
        url = '{}/cgi/crm/approvalTask/action'.format(self.host)
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return json.loads(res.text)



    def completeFlow(self,fsuid,data):
        req={
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId": fsuid,
            "data":data
        } 
        # url = '{}/cgi/crm/v2/special/object/businessFlowComplete'.format(self.host)
        url = '{}/cgi/crm/v2/special/approval/task/action'.format(self.host)
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return json.loads(res.text)



    def objectinfo(self,apiname):
        req={
            "corpAccessToken":self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "includeDetail": True,
            "apiName": apiname
            }
        url = '{}/cgi/crm/v2/object/describe'.format(self.host)
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return res.text
    def objectlist(self):
        req={
            "corpAccessToken":self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid
            }
        url = '{}/cgi/crm/v2/object/list'.format(self.host)
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return res.text
    
    def stamp2date(self,stamp):
        stamp/=1000
        timeArray = time.localtime(stamp)
        otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
        dt_crm = parse(otherStyleTime).date()
        return dt_crm
    def unlock(self,dataid,apiname):   
        req = {
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "data": {
                "dataObjectApiName": apiname,
                "dataIds": [
                    dataid
                ],
                "detailObjStrategy": 1
            }
        }
        url = '{}/cgi/crm/v2/object/unlock'.format(self.host)
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return res.text

    def lock(self,dataid,apiname):   
        req = {
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "data": {
                "dataObjectApiName": apiname,
                "dataIds": [
                    dataid
                ],
                "detailObjStrategy": 1
            }
        }
        url = '{}/cgi/crm/v2/object/lock'.format(self.host)
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return res.text


    def get_process_list(self,apiname,dataid):
        req={
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "data": {
                "entityId": apiname,
                "objectId": dataid
            }
        } 
        url = '{}/cgi/crm/v2/special/getInstanceInfoByObjectId'.format(self.host)
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return json.loads(res.text)

    def get_bpm_list(self,apiname,dataid):
        req={
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "data": {
                "entityId": apiname,
                "objectId": dataid
            }
        } 
        url = '{}/cgi/crm/v2/special/instance/progress'.format(self.host)
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return json.loads(res.text)


    def invalid(self,apiname,dataid):        

        req = {
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "data": {
            "object_data_id": dataid,
            "dataObjectApiName":apiname
            }
        }
        body = json.dumps(req)
        url='{}/cgi/crm/custom/v2/data/invalid'.format(self.host)  
        res = requests.post(url,headers=self.headers,data=body.encode())
        result = json.loads(res.text)
        return result

    def getlog(self,FilterMainID,pageSize=100,pageNumber=0):
        '''
        1	LeadsObj	13	VisitingObj	40	AccountFinInfoObj
        2	AccountObj	16	ContractObj	 	 
        3	ContactObj	17	LeadsPoolObj	 	 
        4	ProductObj	18	HighSeasObj	 	 
        6	RefundObj	20	MarketingEventObj	 	 
        7	SaleActionObj	24	AccountAttObj	 	 
        8	OpportunityObj	26	AccountCostObj	 	 
        9	InvoiceApplicationObj	27	ReturnedGoodsInvoiceProductObj	 	 
        11	SalesOrderObj	28	SalesOrderProductObj	 	 
        12	ReturnedGoodsInvoiceObj	39	AccountAddObj	 	 
        '''
        req={
        "corpAccessToken": self.token,
        "corpId": self.corpid,
        "currentOpenUserId": self.currentuserid,
        "data": {      
            "pageNumber": 0,
            "pageSize": 100,
            "QueryInfo": {
            "FilterMainID": FilterMainID
            }
        }
        }
        url = '{}/cgi/crm/crmLog/query'.format(self.host)
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return json.loads(res.text)

    def getdatalist_new(self,apiname,limit=100):
        
        req={
        "corpAccessToken": self.token,
        "corpId": self.corpid,
        "currentOpenUserId": self.currentuserid,
        "data": {      
            "dataObjectApiName": apiname,# "AccountObj",
            "search_query_info": {
            "offset": 0,
            "limit": 100,
            "filters": [
         
            ]
            }
        }
        }

        url = '{}/cgi/crm/custom/v2/data/query'.format(self.host)
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        obj_res = json.loads(res.text)
        total = obj_res['data']['total']
        result = obj_res['data']['dataList']
        offset=0
        while(len(result)<total):
            offset+=100
            if len(result)>=limit:
                break
            req['data']['search_query_info']['offset']=offset
            pagereq = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
            pageres = json.loads(pagereq.text)
            result+=pageres['data']['dataList']     
            
            print('读取下标{},当前数据量{}'.format(offset,len(result)))    
        return result   

    def getdata(self,dataid,apiname):
        req={
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "data":{
                "dataObjectApiName":apiname
                ,"objectDataId":dataid
            }
        }
        url='{}/cgi/crm/custom/v2/data/get'.format(self.host)  
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return json.loads(res.text)



    def create(self,data,hasSpecifyTime=False,hasSpecifyCreatedBy=False,triggerFlow=False):
        '''
        data 在外面创建吧，格式如下，可以同时带详情，try一下
        {
            "object_data": {
            "owner": [
                "${currentOpenUserId}"
            ],
            "name": "文本值",
            "dataObjectApiName": "customObj__c"
            },
            "details": {}
        }
        '''
        req={
            "corpAccessToken": self.token,
            "hasSpecifyTime":hasSpecifyTime,
            "hasSpecifyCreatedBy":hasSpecifyCreatedBy,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "triggerWorkFlow":triggerFlow,
            "data":data

        }
        url='{}/cgi/crm/custom/v2/data/create'.format(self.host)  
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return json.loads(res.text)



    def objectmod_sp(self,data):
        req={
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "triggerWorkFlow":True,
            "hasSpecifyTime":True,
            "data":{
                "object_data":data
            }

        }
        url='{}/cgi/crm/custom/v2/data/update'.format(self.host)  
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return json.loads(res.text)

    def objectmod(self,data,details={}):
        req={
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "triggerWorkFlow":False,
            "data":{
                "object_data":data,
                "details":details
            }

        }
        url='{}/cgi/crm/custom/v2/data/update'.format(self.host)  
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return json.loads(res.text)
    
    def Lead2Account(self,cuid,is_main,leadid):
        req={
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "triggerWorkFlow":False,
            "data":{
                "dataList":{
                    "AccountObj":{
                        "_id":cuid,
                        "is_main_leads":is_main
                    }
                },
                "combineCRMFeed":True,
                "leadsId":leadid
            }

        }
        url='{}/cgi/crm/v2/leads/transfer'.format(self.host)  
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return json.loads(res.text)
    #获取员工列表
    def getUserList(self):
        body =   {
            "corpAccessToken": self.token,
            "corpId": self.corpid
            ,'departmentId':999999
            ,'fetchChild':True
        }
        url = f'{self.host}/cgi/user/list'
        res = requests.post(url,headers=self.headers,data=json.dumps(body,ensure_ascii=True).encode())
        result = json.loads(res.text)
        return result

    def getuserinfo(self,userid):
        body =   {
            "corpAccessToken": self.token,
            "corpId": self.corpid
            ,"openUserId":userid
            ,"showDepartmentIdsDetail":True
        }
        url = f'{self.host}/cgi/user/get'
        res = requests.post(url,headers=self.headers,data=json.dumps(body,ensure_ascii=True).encode())
        result = json.loads(res.text)
        return result
        
    
    def getparent(self,cusid):
        cus = self.getdata(cusid,'AccountObj')
        if 'parent_account_id' in cus['data']:
            return self.getdata(cus['data']['parent_account_id'],'AccountObj')



    def getdatalist(self,apiname,limit=100,filters=[]):
        
        req={
        "corpAccessToken": self.token,
        "corpId": self.corpid,
        "currentOpenUserId": self.currentuserid,
        "data": {      
            "dataObjectApiName": apiname,# "AccountObj",
            "search_query_info": {
            "offset": 0,
            "limit": 100,
            "filters": filters
            }
        }
        }

        url = '{}/cgi/crm/custom/v2/data/query'.format(self.host)
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        obj_res = json.loads(res.text)
        if obj_res['errorCode']==0:
            total = obj_res['data']['total']
            result = obj_res['data']['dataList']
            offset=0
            while(len(result)<total):
                if offset>=limit:break
                offset+=100
                req['data']['search_query_info']['offset']=offset
                pagereq = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
                pageres = json.loads(pagereq.text)
                result+=pageres['data']['dataList']     
                print('读取下标{},当前数据量{}'.format(offset,len(result)))    
            return result   
        else:
            print(obj_res)
            return []