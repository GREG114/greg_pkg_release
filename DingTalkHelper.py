import json
import time
import requests
import datetime


class DingTalkHelper:
    
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

    def __init__(self,appsecret,appkey,agentid="",userid=''):
        self.host = 'https://oapi.dingtalk.com'
        self.headers={'Content-Type': 'application/json'}
        self.userid=userid
        self.agentid=agentid
        url = self.host+'/gettoken?appsecret={}&appkey={}'.format(appsecret,appkey)
        result = requests.get(url)
        result = json.loads(result.text)
        self.token = result['access_token']
        

    def getleavetimebynames(self,from_date,to_date,userid,leave_names): 
        from_date = datetime.datetime.strftime(from_date,'%Y-%m-%d %H:%M:%S')
        to_date = datetime.datetime.strftime(to_date,'%Y-%m-%d %H:%M:%S')
        # starttuple =int(time.mktime(start.timetuple()))*1000
        # endtuple =int(time.mktime(end.timetuple()))*1000
        url ='https://oapi.dingtalk.com/topapi/attendance/getleavetimebynames?access_token={}'.format(self.token)
        obj = { 
                'userid':userid,
                'leave_names':leave_names,
                'from_date':from_date,
                'to_date':to_date
            }
        source = requests.post(url,headers=self.headers,data = json.dumps(obj,ensure_ascii=True).encode())
        result = json.loads(source.text)
        return result


    def queryonjob(self,status_list,offset,size):
        '''
        https://developers.dingtalk.com/document/app/intelligent-personnel-update-employee-file-information
        '''
        req={
        'status_list':status_list,
        'offset':offset,
        'size':size
        }
        data = json.dumps(req)
        api_path ='https://oapi.dingtalk.com/topapi/smartwork/hrm/employee/queryonjob?access_token={}'.format(self.token)
        result = requests.post(api_path,headers=self.headers,data=data.encode())
        result = json.loads(result.text)
        return result
    
    def queryonjob(self,status_list,offset,size):
        req={
        'status_list':status_list,
        'offset':offset,
        'size':size
        }
        data = json.dumps(req)
        api_path ='https://oapi.dingtalk.com/topapi/smartwork/hrm/employee/queryonjob?access_token={}'.format(self.token)
        result = requests.post(api_path,headers=self.headers,data=data.encode())
        result = json.loads(result.text)
        return result

    def departmentInfo(self,dept_id):
        req={
        'dept_id':dept_id
        }
        data = json.dumps(req)
        api_path ='https://oapi.dingtalk.com/topapi/v2/department/get?access_token={}'.format(self.token)
        result = requests.post(api_path,headers=self.headers,data=data.encode())
        result = json.loads(result.text)
        return result

    def employeelist(self,userid_list,agentid,field_filter_list=None):
        req={
            'userid_list':userid_list,
            'agentid':agentid
        }
        if field_filter_list!=None:
            req['field_filter_list']=field_filter_list
        data = json.dumps(req)
        api_path ='https://oapi.dingtalk.com/topapi/smartwork/hrm/employee/v2/list?access_token={}'.format(self.token)
        result = requests.post(api_path,headers=self.headers,data=data.encode())
        result = json.loads(result.text)
        return result


    def sendMsg(self,data):
        data = json.dumps(data,ensure_ascii=True)
        api_path ='https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?access_token={}'.format(self.token)
        result = requests.post(api_path,headers=self.headers,data=data.encode())
        result = json.loads(result.text)
        return result

    def withdrawProc(self,piid,opuser,remark):
        '''
        撤回流程方法
        piid:流程实体id
        '''
        api_path = 'https://oapi.dingtalk.com/topapi/process/instance/terminate?access_token={}'.format(self.token)
        obj={
            'request':{
            'is_system':False
            ,'process_instance_id':piid
            ,'operating_userid':opuser
            ,'remark':remark
            }
        }
        data = json.dumps(obj, ensure_ascii=True)
        res = requests.post(api_path, headers=self.headers, data=data.encode())
        res = json.loads(res.text)
        return res

    def performProc(self,procid,originator_user_id,dept_id,form_component_values):
        '''
        发起流程的接口
        procid:流程模板id
        originator_user_id:发起人用户id，注意是字符串格式，部分用户首字母为0
        dept_id:发起人所在部门id
        form_component_values：表单内容，如[{'name': '申请分类', 'value': 'IT支持需求'}, {'name': '详细描述', 'value': '测试使用api调用,为了测试终止流程'}]        
        '''
        api_path = '{}/topapi/processinstance/create?access_token={}'.format(self.host, self.token)
        obj = {
            'process_code': procid,
            'originator_user_id':originator_user_id,
            'dept_id': dept_id,
            'form_component_values':form_component_values            
        }
        data = json.dumps(obj, ensure_ascii=True)
        res = requests.post(api_path, headers=self.headers, data=data.encode())
        res = json.loads(res.text)
        return res

    def getleavestatus(self,userid_list,start,end,offset=0,size=20):
        '''
        批量获取请假状态
        支持最多180天的查询
    
        '''
        url = self.host+'/topapi/attendance/getleavestatus?access_token={}'.format(self.token)           
        starttuple =int(time.mktime(start.timetuple()))*1000
        endtuple =int(time.mktime(end.timetuple()))*1000
        obj={
            'userid_list':userid_list
            ,'start_time':starttuple
            ,'end_time':endtuple
            ,'offset':offset
            ,'size':size
        }
        source = requests.post(url,headers=self.headers,data = json.dumps(obj).encode())
        result = json.loads(source.text)
        return result

    def searchProcId(self,procname):
        '''
        允许使用关键字获取流程ID,返回的是一个列表
        '''
        res = self.getProcIdList(0)
        pds = res['result']['process_list']
        while( 'next_cursor' in res['result']):
            res = self.getProcIdList(res['result']['next_cursor'])
            pds += res['result']['process_list']
        result = list(filter(lambda  x: procname in x['name'],pds))
        return result

    def getProcIdList(self,offset):
        '''
        获取流程id列表的方法,就不开放给用户了
        '''
        url = r'{}/topapi/process/listbyuserid?access_token={}'.format(self.host,self.token)
        obj = {
            'offset':offset
            ,'size':100
        }
        data = json.dumps(obj)
        req = requests.post(url,headers=self.headers,data=data.encode())
        res = json.loads(req.text)
        return res
    def getProcessListBatch(self,start,end,pid,user_list,size=20,cursor=0):        
        starttuple =int(time.mktime(start.timetuple()))*1000
        endtuple =int(time.mktime(end.timetuple()))*1000
        url ='https://oapi.dingtalk.com/topapi/processinstance/listids?access_token={}'.format(self.token)
        obj = { 
            'start_time':starttuple
            ,'cursor':cursor
            ,'end_time':endtuple
            ,'process_code':pid
            ,'size':size
            ,'userid_list':user_list
            }
        source = requests.post(url,headers=self.headers,data = json.dumps(obj).encode())
        result = json.loads(source.text)
        return result

    def getProcessListT(self,start,end,pid,size=20,cursor=0):
        starttuple =int(time.mktime(start.timetuple()))*1000
        endtuple =int(time.mktime(end.timetuple()))*1000
        url ='h en={}'.format(self.token)
        obj = { 
            'start_time':starttuple
            ,'end_time':endtuple
            ,'process_code':pid
            ,'size':size
            ,'cursor':cursor
            }
        source = requests.post(url,headers=self.headers,data = json.dumps(obj).encode())
        result = json.loads(source.text)
        return result

    def getDL(self,pid,file_id):
        obj = {
            "request":{
                'process_instance_id':pid,
                'file_id':file_id
            }
        }
        url='https://oapi.dingtalk.com/topapi/processinstance/file/url/get?access_token={}'.format(self.token)
        source = requests.post(url,headers=self.headers,data = json.dumps(obj).encode())
        result = json.loads(source.text)
        return result


        #获取流程id列表
    def getProcessList(self,start,end,pid):
        '''
        pid不给的话默认就是虚拟机模板
        '''
        starttuple =int(time.mktime(start.timetuple()))*1000
        endtuple =int(time.mktime(end.timetuple()))*1000
        url ='https://oapi.dingtalk.com/topapi/processinstance/listids?access_token={}'.format(self.token)
        obj = { 
            'start_time':starttuple
            ,'end_time':endtuple
            ,'process_code':pid
            ,'size':20
            ,'cursor':0
            }
        source = requests.post(url,headers=self.headers,data = json.dumps(obj).encode())
        result = json.loads(source.text)
        while( not result['errcode'] ==0):
            print('异常，开始时间：{},结束时间：{}，异常信息：{}'.format(start,end,result))
            source = requests.post(url,headers=self.headers,data = json.dumps(obj).encode())
            result = json.loads(source.text)
            return []
        data = result['result']['list']
        while('next_cursor' in result['result']):    
            cursor =result['result']['next_cursor']
            #print(cursor*20)
            obj['cursor']=cursor
            test = requests.post(url,headers=self.headers,data = json.dumps(obj).encode())
            result = json.loads(test.text)  

            while( not result['errcode'] ==0):
                print('异常，开始时间：{},结束时间：{}，异常信息：{}'.format(start,end,result))
                source = requests.post(url,headers=self.headers,data = json.dumps(obj).encode())
                result = json.loads(source.text)
                return []
            data += result['result']['list']
        return data

    def GetProcessDetail(self,processid):
        url='https://oapi.dingtalk.com/topapi/processinstance/get?access_token={}'.format(self.token)
        obj={
            'process_instance_id':processid
        }
        result = requests.post(url,headers=self.headers,data = json.dumps(obj).encode())
        result = json.loads(result.text)
        return result

    def GetReportTemplate(self,userid,template_name="售前支持部工作日志"):
        url='{}/topapi/report/template/getbyname?userid={}&template_name={}&access_token={}'.format(self.host,userid,template_name,self.token)
        req=requests.get(url)
        return req.text

    def GetReportList(self,start,end,userid,template=None):
        rps=[]
        url='{}/topapi/report/list?access_token={}'.format(self.host,self.token)
        starttuple =int(time.mktime(start.timetuple()))*1000
        endtuple =int(time.mktime(end.timetuple()))*1000
        obj = {
            'start_time':starttuple
            ,'end_time':endtuple
            ,'userid':userid
            ,'size':20
            ,'cursor':0
        }
        if not template==None:
            obj['template_name']=template
        data = json.dumps(obj)
        req = requests.post(url,headers=self.headers,data=data.encode())
        res = json.loads(req.text)

        if res['errcode']==0:
            # rps+=list(filter(lambda x:x['template_name']==template,res['result']['data_list']))
            rps+=res['result']['data_list']
            while(res['result']['has_more']):
                obj['cursor']=res['result']['next_cursor']
                data = json.dumps(obj)
                req = requests.post(url,headers=self.headers,data=data.encode())
                res = json.loads(req.text)
                rps+=res['result']['data_list']
                # rps+=list(filter(lambda x:x['template_name']==template,res['result']['data_list']))
            # res=res['result']
        if not template==None:
            rps=list(filter(lambda x:x['template_name']==template,rps))
        return rps

    def GetAttResults(self,workDateFrom,workDateTo,userIdList,offset=0,limit=50):
        '''    
        "workDateFrom": "yyyy-MM-dd HH:mm:ss",
        "workDateTo": "yyyy-MM-dd HH:mm:ss",
        "userIdList":["员工UserId列表"],    // 必填，与offset和limit配合使用
        "offset":0,    // 必填，第一次传0，如果还有多余数据，下次传之前的offset加上limit的值
        "limit":1,     // 必填，表示数据条数，最大不能超过50条
        '''
        obj={
            "workDateFrom": workDateFrom,
            "workDateTo": workDateTo,
            "userIdList":userIdList,  
            "offset":offset,
            "limit":limit
        } 
        path = '{}/attendance/list?access_token={}'.format(self.host,self.token)
        data = json.dumps(obj)
        req = requests.post(path,headers=self.headers,data=data.encode())
        return req



    #宜搭api
    def form_put_yida(self,formInstanceId='',updateFormDataJson=''):
        req={
            "appType" : "APP_R0V8RF60KSCN2W65L50A",
            "systemToken" : "0H866O81PUO4E7N36P8SLCIR78D436B8PE59LC4",
           "userId" : self.userid,
            "formInstanceId" : formInstanceId,
            "useLatestVersion" : True,
            "updateFormDataJson" : updateFormDataJson
        }
        data = json.dumps(req)
        url=f'https://api.dingtalk.com/v1.0/yida/forms/instances?x-acs-dingtalk-access-token={self.token}'
        result = requests.put(url,headers=self.headers,data=data.encode())
        return result.status_code
    
    def form_batchSave_yida(self,formUuid='',formDataJsonList=[],appType="",systemToken='',noExecuteExpression=False,keepRunningAfterException=False,asynchronousExecution=False):
        '''
        noExecuteExpression:是否不触发表单绑定的校验规则、关联业务规则和第三方服务回调。true：不触发
        asynchronousExecution:是否需要宜搭服务端异步执行该任务。true：允许。
        keepRunningAfterException:批量保存多条表单实例数据发生异常时是否跳过异常的表单实例并继续保存下一个表单实例数据。true：跳过
        '''
        req={
        "noExecuteExpression" : noExecuteExpression,
        "keepRunningAfterException":keepRunningAfterException,
        "asynchronousExecution":asynchronousExecution,
        "appType" : appType,
        "systemToken" : systemToken,
        "userId" : self.userid,
        "formUuid" : formUuid,
        "formDataJsonList" : formDataJsonList,
        }
        data = json.dumps(req)
        url=f'https://api.dingtalk.com/v1.0/yida/forms/instances/batchSave?x-acs-dingtalk-access-token={self.token}'
        result = requests.post(url,headers=self.headers,data=data.encode())
        result = json.loads(result.text)
        return result
    def form_getAll_yida(self,uuid,searchFieldJson,apptype,systemtoken):
        result =[]    
        cp=1
        res_targets = self.form_search_yida(apptype,searchFieldJson,uuid,systemtoken)
        result+= res_targets['data']
        while(len(result)< res_targets['totalCount']):
            cp+=1
            res_targets = self.form_search_yida(apptype,searchFieldJson,uuid,systemtoken,currentPage=cp)
            result+= res_targets['data']
        return result
    def form_search_yida(self,appType='',searchFieldJson=''
    ,formUuid='FORM-56666571BUP4QX8E9FHCABGX4W703UA9ZFG9LH'
    ,systemToken="0H866O81PUO4E7N36P8SLCIR78D436B8PE59LC4"
    ,currentPage=1
    ):
        req={
        "appType" : appType,
        "systemToken" : systemToken,
        "userId" : self.userid,
        "formUuid" : formUuid,
        "searchFieldJson" : searchFieldJson,
        "pageSize" : 100,
        "currentPage":currentPage
        }
        data = json.dumps(req)
        url=f'https://api.dingtalk.com/v1.0/yida/forms/instances/search?x-acs-dingtalk-access-token={self.token}'
        result = requests.post(url,headers=self.headers,data=data.encode())
        result = json.loads(result.text)
        return result
    def form_process_start_yida(self,appType="",formDataJson='',processCode='',formUuid='FORM-56666571BUP4QX8E9FHCABGX4W703UA9ZFG9LH',systemToken='0H866O81PUO4E7N36P8SLCIR78D436B8PE59LC4'):
        req={
        "appType" : appType,
        "systemToken" : systemToken,
        "userId" : self.userid,
        "formUuid" : formUuid,
        "formDataJson" : formDataJson,
        "processCode" : processCode,
        }
        data = json.dumps(req)
        url=f'https://api.dingtalk.com/v1.0/yida/processes/instances/start?x-acs-dingtalk-access-token={self.token}'
        result = requests.post(url,headers=self.headers,data=data.encode())
        result = json.loads(result.text)
        return result
    def form_definitions(self,systemToken='0H866O81PUO4E7N36P8SLCIR78D436B8PE59LC4',appType='APP_R0V8RF60KSCN2W65L50A',formUuid='FORM-56666571BUP4QX8E9FHCABGX4W703UA9ZFG9LH'):
        self.headers['x-acs-dingtalk-access-token']=self.token
        url=f'https://api.dingtalk.com/v1.0/yida/forms/definitions/{appType}/{formUuid}?systemToken={systemToken}&userId={self.userid}'
        result = requests.get(url,headers=self.headers)
        result = json.loads(result.text)
        return result
    def form_batchremove_yida(self,formUuid,formInstanceIdList,appType="",systemToken='0H866O81PUO4E7N36P8SLCIR78D436B8PE59LC4',asynchronousExecution=True):
        req={
        "appType" : appType,
        "systemToken" : systemToken,
        "userId" : self.userid,
        "formUuid" : formUuid,
        "formInstanceIdList":formInstanceIdList,
        "asynchronousExecution":asynchronousExecution
        }

        data = json.dumps(req)
        url=f'https://api.dingtalk.com/v1.0/yida/forms/instances/batchRemove?x-acs-dingtalk-access-token={self.token}'
        result = requests.post(url,headers=self.headers,data=data.encode())
        result = json.loads(result.text)
        return result
    def form_batch_update(self,
        appType="",systemToken='0H866O81PUO4E7N36P8SLCIR78D436B8PE59LC4',updateFormDataJson='',formUuid='',formInstanceIdList=[],
        noExecuteExpression=False,ignoreEmpty=True,useLatestFormSchemaVersion=True,asynchronousExecution=True):

        req={
        "noExecuteExpression" : noExecuteExpression,
        "formUuid" : formUuid,
        "updateFormDataJson" : updateFormDataJson,
        "appType" : appType,
        "ignoreEmpty" : ignoreEmpty,
        "systemToken" :  systemToken,
        "useLatestFormSchemaVersion" : useLatestFormSchemaVersion,
        "asynchronousExecution" : asynchronousExecution,
        "formInstanceIdList" : formInstanceIdList,
        "userId" : self.userid,
        }
        data = json.dumps(req)
        url=f'https://api.dingtalk.com/v1.0/yida/forms/instances/components?x-acs-dingtalk-access-token={self.token}'
        result = requests.put(url,headers=self.headers,data=data.encode())
        result = json.loads(result.text)
        return result
