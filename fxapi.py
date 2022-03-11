import requests
import json
import time
import random
import threading
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

    
    def BatchCreate(self,total):
        tc=0
        def data_create(obj):
            nonlocal tc
            req = {
                'object_data':obj
            }
            while True:
                try:
                    res = self.create(req,True)
                    if res['errorCode']==0:                        
                        tc-=1
                        break
                    else:
                        print(res)
                except Exception as Ex:
                    print(Ex)
                    print(obj)
                    time.sleep(3)

        ts=[]
        for d in total:
            t=threading.Thread(target=data_create,args=(d,))
            while tc>=35:
                # print('防止阻塞') 
                time.sleep(5)
            ts.append(t)
            t.start()
            tc+=1
        for t in ts:
            t.join()  


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




    def getobjlog(self,apiname,dataid):
        req ={
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId":self.currentuserid,
            "data": {
            "apiName": apiname,
                "objectId": dataid,
                "operationalType":"system",
                "pageNumber": 1,
                "pageSize": 200
            }
        }
        data = json.dumps(req)
        url = r'https://open.fxiaoke.com/cgi/crm/v2/object/getNewLogInfoListForWeb'
        res = requests.post(url,headers = self.headers,data = data.encode())
        result = json.loads(res.text)
        recordList = result['data']['modifyRecordList']
        pagecount = result['data']['pageInfo']['pageCount']
        page=1
        while page<pagecount:
            page+=1
            req['data']['pageNumber']=page
            url = r'https://open.fxiaoke.com/cgi/crm/v2/object/getNewLogInfoListForWeb'
            res = requests.post(url,headers = self.headers,data = data.encode())
            result = json.loads(res.text)
            recordList += result['data']['modifyRecordList']

        return recordList

    def clear_xiezuo(self,apiname,id):
        req={
            "corpAccessToken":self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "apiName": apiname,
            "data": {
                "dataID": id,
                "teamMemberInfos":[
                ]
            }
        }
        data = json.dumps(req)
        res = requests.post('https://open.fxiaoke.com/cgi/crm/team/edit',headers=self.headers,data=data.encode())
        result = json.loads(res.text)
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

    def cancelapproval(self,objectid,apiname,reson):
        req={
        "corpAccessToken": self.token,
        "corpId": self.corpid,
        "currentOpenUserId": self.currentuserid,
        "data": {
            "objectId": objectid,
            "entityId": apiname,
            "opinion": "取消审批"
        }
        } 
        url = '{}/cgi/crm/v2/special/approval/instance/cancel'.format(self.host)
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
        return json.loads(res.text)
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
        return json.loads(res.text)

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
        return json.loads(res.text)


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
        try:
            res = res = requests.post(url,headers=self.headers,data=body.encode(),timeout=10)
            return json.loads(res.text)
        except Exception as ex:
            raise(ex)    

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
        try:
            res = requests.post(url,headers=self.headers,data=json.dumps(req).encode(),timeout=10)
            return json.loads(res.text)                
        except Exception as ex:
            raise(ex)       



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

    def changeOwner(self,data,dataObjectApiName):
        '''
        "data": {
            "dataObjectApiName":"object_Nyeoj__c",
            "Data": [
            {
                "objectDataId": "5a9914fcf125ae0a1axxxxxx",
                "ownerId": [
                "FSUID_7B8A3925E40FA68630C0D7E9C3XXXXXX"
                ]
            }
            ]
        }
        '''
        req={
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "data":{
                "Data":data,
                "dataObjectApiName":dataObjectApiName
            }

        }
        url='{}/cgi/crm/custom/v2/data/changeOwner'.format(self.host)  
        res = requests.post(url,headers=self.headers,data=json.dumps(req).encode())
        return json.loads(res.text)


    def objectmod(self,data,details={},trigger=False):
        '''
        updateobj={
            '_id':bid,
            'dataObjectApiName':'QuoteObj',
            'account_id':cuid
        }   
        '''
        req={
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "triggerWorkFlow":trigger,
            "data":{
                "object_data":data,
                "details":details
            }

        }
        url='{}/cgi/crm/custom/v2/data/update'.format(self.host)  
        try:
            res = requests.post(url,headers=self.headers,data=json.dumps(req).encode(),timeout=20)
            # print(req)
            return json.loads(res.text)
        except Exception as ex:
            raise(ex)     
    
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

    def delete(self,dataObjectApiName,idList):
        req = {
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId": self.currentuserid,
            "data": {
                "idList": idList,
                "dataObjectApiName": dataObjectApiName
            }
        }
        data=json.dumps(req,ensure_ascii=True)
        res = requests.post(f'{self.host}/cgi/crm/custom/v2/data/delete',headers=self.headers,data=data.encode())
        result = json.loads(res.text)
        return result

    def getData_thread(self,apiname,filters=[]):
        lock=threading.Lock()        
        datapool=[]
        ts=[]   
        def getdatalist(offset,apiname,filters):
            nonlocal datapool,lock          
            res = self.query(apiname,filters=filters,limit=200,offset=offset)
            while(res['errorCode']!=0):
                print('读取速度过快，缓缓')
                time.sleep(8)
                res = self.query(apiname,filters=filters,limit=200,offset=offset)
            datalist = res['data']['dataList']
            lock.acquire()
            datapool+=datalist
            print(len(datapool))
            lock.release()
        
        if filters==[]:            
            filters=[
            {
                'field_name':'life_status',
                'field_values':['normal'],
                'operator':'EQ'
            }    ]        
        res = self.query(apiname,limit=1,filters=filters)
        if res['errorCode']!=0:
            return res

        total = res['data']['total']
        offset=0
        while(offset<=total):       
            t=threading.Thread(target=getdatalist,args=(offset,apiname,filters))
            ts.append(t)
            t.start()        
            offset+=200
        for t in ts:
            t.join()
        return datapool


    def addteamMember(self,apiName,dataids,teamMemberEmployee):
        '''
        teamMemberEmployee:list<str>
        dataids:list<str>
        '''       
        body =   {
            "corpAccessToken": self.token,
            "corpId": self.corpid,
            "currentOpenUserId":self.currentuserid,
            "apiName":apiName,
            "data":{
                'dataIDs': dataids
                ,'teamMemberEmployee':teamMemberEmployee    
                ,'teamMemberRole': 4
                ,'teamMemberPermissionType': 2              
            }           
        }
        url = f'{self.host}/cgi/crm/team/add'
        res = requests.post(url,headers=self.headers,data=json.dumps(body,ensure_ascii=True).encode())
        result = json.loads(res.text)
        return result 

    
    def getparent(self,cusid):
        cus = self.getdata(cusid,'AccountObj')
        if 'parent_account_id' in cus['data']:
            return self.getdata(cus['data']['parent_account_id'],'AccountObj')

    def query(self,apiname,offset=0,limit=100,filters=[]):
        req={
        "corpAccessToken": self.token,
        "corpId": self.corpid,
        "currentOpenUserId": self.currentuserid,
        "data": {      
            "dataObjectApiName": apiname,# "AccountObj",
            "search_query_info": {
            "offset": offset,
            "limit": limit,
            "filters": filters
            }
        }
        }
        url = '{}/cgi/crm/custom/v2/data/query'.format(self.host)
        retry=0
        while retry<3:
            try:
                res = requests.post(url,headers=self.headers,data=json.dumps(req).encode(),timeout=8)
                return json.loads(res.text)
            except Exception as ex:                
                retry+=1
                print(ex)       
        return []





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