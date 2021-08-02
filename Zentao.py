import requests
import json
from hashlib import md5



class Zentao(object):


    def __init__(self, host, account, password):
        self.host = host
        self.session_id = ''
        self.params = {}
        self.account = account
        self.password = password

        self._get_session_id()
        self.login()

    def _get_session_id(self):
        api_path = "/zentao/api-getsessionid.json"
        response = requests.get(self.host + api_path)
        result = self._get_zentao_result(response.json())
        self.session_id = result['sessionID']
        self.params[result['sessionName']] = self.session_id

    def login(self):
        api_path = '/zentao/user-login.json'
        data = {
            'account': self.account,
            'password': self.password,
        }
        result = requests.post(self.host + api_path, data=data, params=self.params).json()
        if result['status'] == 'success':
            print('zentao 登陆成功')
        else:
            print(result)

    @staticmethod
    def _get_zentao_result(result):
        if result['status'] == 'success' and md5(result['data'].encode()).hexdigest() == result['md5']:
            data = json.loads(result['data'])
            return data
        return result

    def zentao_get(self, api_path):
        response = requests.get(self.host + api_path, self.params)
        #print(response.content)
        result = response.json()
        # print(result)
        return self._get_zentao_result(result)

    def zentao_post(self, api_path, data=None, json_data=None):
        response = requests.post(self.host + api_path, data=data, json=json_data, params=self.params)

        return self._get_zentao_result(response.json())

    #根据用户获取BUG，可以定义状态
    #status: resolvedBy、openedBy
    #userid:禅道里的用户id
    def get_user_bugs(self,userid,status):
        bugs=[]        
        #取所有需要的数据：任务和BUG
        pageid=1
        api_path='/zentao/user-bug-{}-{}--all-200.json'.format(userid,status)
        data=self.zentao_get(api_path)
        #用列表生成式将用户的任务晒出来放进我们的list中
        bugs+=list(x for x in data['bugs'])
        pageid=1
        #如果还有更多页就继续
        while(pageid<int(data['pager']['pageTotal'])):

            pageid+=1
            api_path='/zentao/user-bug-{}-{}--all-200-{}.json'.format(userid,status,pageid)
            data=self.zentao_get(api_path)         
            bugs+=list(x for x in data['bugs'])
        return bugs


    #查询用户解决的BUG
    def get_userBugs(self,user):
        usertasks=[]        
        #取所有需要的数据：任务和BUG
        pageid=1
        api_path='/zentao/user-bug-{}-resolvedBy--all-200.json'.format(user['userid'])
        tasks=self.zentao_get(api_path)
        #用列表生成式将用户的任务晒出来放进我们的list中
        usertasks+=list(x for x in tasks['bugs'])
        pageid=1
        #如果还有更多页就继续
        while(pageid<int(tasks['pager']['pageTotal'])):

            pageid+=1
            api_path='/zentao/user-bug-{}-resolvedBy--all-200-{}.json'.format(user['userid'],pageid)
            tasks=self.zentao_get(api_path)      
            usertasks+=list(x for x in tasks['bugs'])
        return usertasks



    #根据用户获取需求【用户，含['userid']字段的字典即可】【catchfield为判断字段，是创建还是指派给之类的】
    def get_userRequres(self,user,catchfield):
        requires=[]        
        #取所有需要的数据：任务和BUG
        pageid=1
        api_path='/zentao/user-story-{}-{}--all-200.json'.format(user['userid'],catchfield)
        tasks=self.zentao_get(api_path)
        #用列表生成式将用户的任务晒出来放进我们的list中
        requires+=list(x for x in tasks['stories'])
        pageid=1
        #如果还有更多页就继续
        while(pageid<int(tasks['pager']['pageTotal'])):
            pageid+=1
            api_path='/zentao/user-story-{}-{}--all-200-{}.json'.format(user['userid'],catchfield,pageid)
            tasks=self.zentao_get(api_path)      
            requires+=list(x for x in tasks['stories'])
        return requires  

    #查询用户提交的的BUG
    def get_userPushBugs(self,user):
        usertasks=[]        
        #取所有需要的数据：任务和BUG
        pageid=1
        api_path='/zentao/user-bug-{}-openedBy--all-200.json'.format(user['userid'])
        tasks=self.zentao_get(api_path)
        #用列表生成式将用户的任务晒出来放进我们的list中
        usertasks+=list(x for x in tasks['bugs'])
        pageid=1
        #如果还有更多页就继续
        while(pageid<int(tasks['pager']['pageTotal'])):
            pageid+=1
            api_path='/zentao/user-bug-{}-openedBy--all-200-{}.json'.format(user['userid'],pageid)
            tasks=self.zentao_get(api_path)      
            usertasks+=list(x for x in tasks['bugs'])
        return usertasks
    #获取产品列表
    def get_products(self):
        api_path='/zentao/product-index.json'
        result = self.zentao_get(api_path)
        products = result['products']
        return products
    #获取迭代信息？
    def get_project(self,projectId):
        api_path='/zentao/project-view-{}.json'.format(projectId)
        data = self.zentao_get(api_path)
        return data



    #根据用户获取任务【用户，含['userid']字段的字典即可】【catchfield为判断字段，是创建还是指派给之类的】
    def get_userTasks(self,user,catchfield):
        tasks=[]        
        #取所有需要的数据：任务和BUG
        pageid=1
        api_path='/zentao/user-task-{}-{}-all-200.json'.format(user['userid'],catchfield)
        result=self.zentao_get(api_path)
        #用列表生成式将用户的任务晒出来放进我们的list中
        tasks+=list(result['tasks'][x] for x in result['tasks'])
        pageid=1
        #如果还有更多页就继续
        while(pageid<int(result['pager']['pageTotal'])):
            pageid+=1
            api_path='/zentao/user-task-{}-{}-all-200-{}.json'.format(user['userid'],catchfield,pageid)
            result=self.zentao_get(api_path)         
            tasks+=list(result['tasks'][x] for x in result['tasks'])

        return tasks

    def get_dept_list(self):
        """
        获取部门列表
        :return:
        """
        api_path = "/zentao/dept-browse-.json"
        data = self.zentao_get(api_path)
        return data['sons']
    #默认一千个任务，暂时不分页
    def get_project_tasks(self,projectID):

        api_path='/zentao/project-task-{}-all-0---4000.json'.format(projectID)
        data=self.zentao_get(api_path)
        return data
    #获取所有迭代
    #doing 进行中
    #closed 已关闭
    def get_all_projects(self,status):
        page=1
        api_path = '/zentao/project-all-{}-----200-{}.json'.format(status,page)
        data = self.zentao_get(api_path)
        projects=data['projectStats']
        pageTotal=data['pager']['pageTotal']
        while(page<pageTotal):
            page+=1
            api_path = '/zentao/project-all-{}-----200-{}.json'.format(status,page)
            data = self.zentao_get(api_path)
            projects+=data['projectStats']
        return projects
    #根据产品获取迭代,第二个参数是状态
    def get_projects(self,productid,status):
        api_path='/zentao/project-all-{}---{}--1000-1.json'.format(status,productid)
        data=self.zentao_get(api_path)
        return data['projectStats']
    def get_stories(self,projectID):
        api_path='/zentao/project-story-{}.json'.format(projectID)
        data=self.zentao_get(api_path)
        return data#['stories']
    #获取用户列表，上限1000
    def get_userlist(self):        
        api_path='/zentao/company-browse-0-bydept-id-0-1000.json'
        data = self.zentao_get(api_path)
        return data['users']

    def get_story(self,storyId):
        api_path='/zentao/story-view-{}.json'.format(storyId)
        data=self.zentao_get(api_path)
        return data

    def get_product_stories(self,productId,status):
        #/zentao/product-browse-1--closed-0--0-35-1
        api_path='/zentao/product-browse-{}--{}-0--0-200.json'.format(productId,status)
        data=self.zentao_get(api_path)
        return data

    #获取禅道上bug列表，一次性拉完。。。
    def get_bug_list(self,product):
        api_path = '/zentao/bug-browse-'+product+'-0-all-0--0-1-1.json'
        bugcount = self.zentao_get(api_path)['pager']['recTotal']
        api_path = '/zentao/bug-browse-'+product+'-0-all-0--0-' + str(bugcount) + '-1.json'   #api_path=
                                                                                    #'/zentao/bug-browse-1-0-all-0--'+str(bugcount)+'-'+str(bugcount)+'-1.json'
        data = self.zentao_get(api_path)
        return data
    #project-bug-1-status,id_desc-0--0-65-200-1.html
    #/zentao/project-bug-[projectID]-[orderBy]-[build]-[type]-[param]-[recTotal]-[recPerPage]-[pageID].json
    #根据迭代取bug,不分页，最多取1000个
    def get_bug_byproject(self,project):
        api_path = '/zentao/project-bug-'+project+'--0--0--1000.json'  
        data = self.zentao_get(api_path)
        return data

    
    def getConsumed(self,taskid):
        api_path='/zentao/task-recordEstimate-{}.json'.format(taskid)
        data = self.zentao_get(api_path)
        return data

