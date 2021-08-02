import requests
import json
import time
class AkCrm():
    '''
    host是爱客的api地址,比如钉钉版的是https://dingtalk.e.ikcrm.com/
    然后是用户名和密码,登陆成功后会生成一个essential字符串,在每次获取api数据的时候都要用
    商机编号的字段是text_asset_2915aa'  
    '''

    def __init__(self,host='https://dingtalk.e.ikcrm.com',userid='',password='',test=False):
        
        self.headers={'Content-Type': 'application/json'}
        self.login=userid
        self.password=password
        self.host=host
        self.essential=None
        self.test=test
        url = host+'/api/v2/auth/login'
        obj = {'device':'dingtalk','login':self.login,'password':self.password,'version_code':'9.9.9'}
        loginresult = requests.post(url,obj)
        while loginresult.status_code==429:
            print('遇到强制阻塞,正在虚与委蛇')
            time.sleep(5)
            loginresult = requests.post(url,obj)
        loginresult=json.loads(loginresult.text)
        if 'data' in loginresult:
            if 'user_token' in loginresult['data']:
                self.token= loginresult['data']['user_token']
                self.essential='?user_token={}&version_code=9.9.9&device=open_api'.format(self.token)
                print('登陆爱客CRM成功,已经获得令牌')
    
    def contract_modify(self,obj,id):
        '''
        修改合同的方法,只需要合同的对象和id就可以
        合同对象格式如下,去elk中找字段名
        obj:{
            'contract':{
                '字段':'值'
            }
        }
        '''
        data = json.dumps(obj,ensure_ascii=True)
        apipath='{}/api/v2/contracts/{}{}'.format(self.host,id,self.essential)
        req = requests.put(apipath,headers=self.headers,data=data.encode())
        while req.status_code==429:
            print('遇到强制阻塞,正在虚与委蛇')
            time.sleep(5)
            req = requests.put(apipath,headers=self.headers,data=data.encode())
        return json.loads(req.text)

    def opportunity_modify(self,obj,id):
        '''
        修改商机的方法,只需要合同的对象和id就可以
        合同对象格式如下,去elk中找字段名
        obj:{
            'contract':{
                '字段':'值'
            }
        }
        '''
        data = json.dumps(obj,ensure_ascii=True)
        apipath='{}/api/v2/opportunities/{}{}'.format(self.host,id,self.essential)
        req = requests.put(apipath,headers=self.headers,data=data.encode())
        while req.status_code==429:
            print('遇到强制阻塞,正在虚与委蛇')
            time.sleep(5)
            req = requests.put(apipath,headers=self.headers,data=data.encode())
        return json.loads(req.text)


    def customer_modify(self,obj,id):
        '''
        修改合同的方法,只需要合同的对象和id就可以
        合同对象格式如下,去elk中找字段名
        obj:{
            'customer':{
                '字段':'值'
            }
        }
        '''
        data = json.dumps(obj,ensure_ascii=True)
        apipath='{}/api/v2/customers/{}{}'.format(self.host,id,self.essential)
        req = requests.put(apipath,headers=self.headers,data=data.encode())
        while req.status_code==429:
            print('遇到强制阻塞,正在虚与委蛇')
            time.sleep(5)
            req = requests.put(apipath,headers=self.headers,data=data.encode())
        return json.loads(req.text)


    def checkins(self):
        apipath='/api/v2/checkins'
        req = requests.get('{}{}{}&per_page=4'.format(self.host,apipath,self.essential))
        return json.loads(req.text)

    def departs(self):
        apipath='{}/api/v2/user/department_list{}'.format(self.host,self.essential)
        req=requests.get(apipath)
        return json.loads(req.text)

    def users(self,dpid=''):
        apipath='{}/api/v2/user/list{}&per_page=100&department_id={}'.format(self.host,self.essential,dpid)
        req=requests.get(apipath)
        while req.status_code==429:
            print('遇到强制阻塞,正在虚与委蛇')
            time.sleep(5)
            req = requests.get(apipath)
        result = json.loads(req.text)
        return result

    def ak_getlogs(self,page=1,start='2020-09-15',model='opportunity',end='2020-12-31'):        
        apipath = '/api/v2/revisit_logs/new_index'
        url = self.host +apipath+self.essential+'&per_page=200&page={}&start_date={}&end_date={}&date=other&loggable_type={}'.format(page,start,end,model)
        result = requests.get(url)
        while result.status_code==429:
            print('遇到强制阻塞,正在虚与委蛇')
            time.sleep(5)
        result = json.loads(result.text)
        return result


    def ak_putlog(self,log):        
        '''
        log:跟进记录，dict，要求形式如下
        log={
            'revisit_log':{
                'loggable_id':opid
                ,'content':'test'
                ,'loggable_type':'Opportunity'
                ,'real_revisit_at':str(datetime.datetime(2020,12,6))                
            }
        }
            loggable_id:关联对象的id
            loggable_type:跟进关联的模型：[Opportunity,Contract,Contact,Customer,Lead]
        return：post之后获得的结果
        '''
        api_path = '{}/api/v2/revisit_logs?{}'.format(self.host,self.essential)
        data = json.dumps(log,ensure_ascii=True)
        req = requests.post(api_path,headers=self.headers,data=data.encode())
        res=json.loads(req.text)
        return res


    def ak_getreports(self,page=1):
        apipath = '{}/api/v2/schedule_reports{}&tab_type=sub&per_page=100&page={}'.format(self.host,self.essential,page)
        result = requests.get(apipath)
        while result.status_code==429:
            print('遇到强制阻塞,正在虚与委蛇')
            time.sleep(5)
            result = requests.get(apipath)
        result = json.loads(result.text)
        reports = result['data']    
        return reports
        
    def getData(self,model,id):
        '''
        单条数据详情获取
        model:
            商机:opportunities
            客户:customers
            合同:contracts
        '''
        url = '{}/api/v2/{}/{}'.format(self.host,model,str(id)+self.essential)
        result = requests.get(url)
        while result.status_code==429:
            print('收到阻塞，正在虚与委蛇')
            time.sleep(5)
            result = requests.get(url)
        if result.status_code==200:
            data = json.loads(result.text)
            return data
        return None
    def getDataPerPage(self,model,page=0):
        url = '{}/api/v2/{}&per_page=100&page={}'.format(self.host,model+self.essential,page)
        result = requests.get(url)
        if result.status_code ==200:
            result = json.loads(result.text)
            return result
        else:
            return None

    def getreport(self,id):
        apipath='{}/api/v2/schedule_reports/{}{}'.format(self.host,id,self.essential)
        result = requests.get(apipath)
        while result.status_code==429:
            print('遇到强制阻塞,正在虚与委蛇')
            time.sleep(5)
            result = requests.get(apipath)
        result = json.loads(result.text)
        reports = result['data']    
        return reports
    def getAllData(self,model):
        '''
        数据列表获取
        model:
            商机:opportunities
            客户:customers
            合同:contracts
        '''
        url = '{}/api/v2/{}&per_page=100'.format(self.host,model+self.essential)
        firstpage=requests.get(url).text
        result = json.loads(firstpage)
        data=result['data'][model]
        has_more=result['data']['has_next_page']

        if self.test:
            has_more=False
        page=1
        errortime=0
        while(has_more):
            print('准备获取第{}页数据'.format(page))
            page+=1
            result =requests.get(url+'&page={}'.format(page))            
            if result.status_code==200:
                context=result.text
                result = json.loads(context)
                has_more = result['data']['has_next_page']
                data += result['data'][model]     
            else:
                print(result.reason)
                page-=1
                time.sleep(5)
            if errortime >5:
                print('出现错误过多,程序终止')
                return 'error,出现错误过多,程序终止'
            #测试用
        return data

    def opvalid(self,op,valid):
        url = '{}/api/v2/opportunities/{}'.format(self.host,op['id'])+self.essential
        # print(url)
        stage=op['stage_mapped']
        obj = {'opportunity':{
            'text_asset_6f4e3b':'sel_4d1f'
            }
        }
        if valid:
            obj['opportunity']['text_asset_6f4e3b']='sel_7179'
        data = json.dumps(obj,ensure_ascii=True)
        result = requests.put(url,headers=self.headers,data=data.encode())

        while result.status_code ==429:
            print('被阻塞，稍等')
            time.sleep(5)
            result= requests.put(url,headers=self.headers,data=data.encode())

        if not result.status_code==200:            
            print(result.text)
        else:
            print('商机{},状态为{}，标记为{}'.format(op['id'],stage,valid))

    def getallchild(self,dps,dpid):
        '''
        dps:字典,此处以名称为索引
        递归方式获取所有子部门,前提是字典每一个子项都需要有id和parent_id
        '''
        result =[]
        targets = list(filter(lambda x:dps[x]['parent_id']==dpid,dps))
        targets = list(dps[x] for x in targets)
        result +=targets
        for target in targets:
            childtargets = self.getallchild(dps,target['id'])
            result+=childtargets        
        return result




