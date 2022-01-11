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

    def __init__(self,appsecret,appkey,agentid=''):
        self.agentid=agentid
        self.host = 'https://oapi.dingtalk.com'
        self.headers={'Content-Type': 'application/json'}
        url = self.host+'/gettoken?appsecret={}&appkey={}'.format(appsecret,appkey)
        result = requests.get(url)
        result = json.loads(result.text)
        self.token = result['access_token']
        


    def task_create(self,pid,activity_id='',tasks=[]):#钉钉流程里创建待办，怀疑结束的流程无法操作，暂时没用
        req={
            'request':{
            'agentid':self.agentid
            ,'process_instance_id':pid
            ,"activity_id": activity_id
            ,'tasks':tasks
            }
            }
        url = f'https://oapi.dingtalk.com/topapi/process/workrecord/task/create?access_token={self.token}'        
        res = requests.post(url,headers=self.headers,data = json.dumps(req,ensure_ascii=True).encode())
        result = json.loads(res.text)
        return result


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


    def querydimission(self,offset,size):
        '''
        https://open.dingtalk.com/document/orgapp-server/intelligent-personnel-query-company-turnover-list
        '''
        req={
        'offset':offset,
        'size':size
        }
        data = json.dumps(req)
        api_path ='https://oapi.dingtalk.com/topapi/smartwork/hrm/employee/querydimission?access_token={}'.format(self.token)
        result = requests.post(api_path,headers=self.headers,data=data.encode())
        result = json.loads(result.text)
        return result

    def queryonjob(self,status_list,offset,size):
        '''
        https://open.dingtalk.com/document/orgapp-server/intelligent-personnel-query-the-list-of-on-the-job-employees-of-the
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

    def listdimission(self,userid_list):
        req={
            'userid_list':userid_list,
        }
        data = json.dumps(req)
        api_path ='https://oapi.dingtalk.com/topapi/smartwork/hrm/employee/listdimission?access_token={}'.format(self.token)
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
        url ='https://oapi.dingtalk.com/topapi/processinstance/listids?access_token={}'.format(self.token)
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
