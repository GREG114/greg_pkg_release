from k3cloud_webapi_sdk.main import K3CloudApiSdk
import json

customer_mod='BD_Customer_All'
othermetrial = 'BOS_ASSISTANTDATA_DETAIL'

class k3helper(object):
    def __init__(self,conf,host):
        self.api = K3CloudApiSdk(host)
        self.api.Init(conf)


    def SaveASSISTANTDATA(self, FNumber, FDataValue, FID):
        req = {
            'FormId': "BOS_ASSISTANTDATA_DETAIL",
            'Model':
            {
                'FNumber': FNumber,
                'FDataValue': FDataValue,
                'Fid':  {
                    'FID': FID
                }
            }
        }        
        res = self.api.Save("BOS_ASSISTANTDATA_DETAIL",req)
        return res

    def GetNewAssID(self,fid):
        '''
        fid是辅助资料的类型id,帐套变更之后会变,注意去数据库里查
        资料类别,通过数据库T_BAS_ASSISTANTDATA_L 
        '''
        req = {
            'FormId': "BOS_ASSISTANTDATA_DETAIL",
            'Fieldkeys': "FDATAVALUE,FNUMBER,FID",
            'FilterString': f"fid='{fid}'"
        }
        res = self.api.ExecuteBillQuery(req)
        assets = json.loads(res)
        assets = sorted(assets,key=lambda x:int(x[1]),reverse=True)
        if len(assets)>0:
            no_asset = assets[0][1]
            no_asset = int(no_asset)+1
            no_asset = str(no_asset).zfill(5)
            return no_asset
        else:
            return '00001'

    def kquery(self,formid,fields,firstrow=0,filterstring='',perpage=0):
        '''
        标准金蝶单页查询方法
        formid:表单类型
        fields:需要展示的字段,需要使用元数据查询获取
        filterstring:筛选语句   字段名='[值]'
        firstrow:开始行,默认为0
        limit:每页数据量,默认100
        '''
        req = {
            'FormId': formid,
            'FieldKeys': fields,
            'FilterString': filterstring,
            'StartRow': firstrow,
            'Limit': perpage
        }
        
        result = json.loads(self.api.ExecuteBillQuery(req))
        return result
    
    #金蝶全量查询,自动翻页,需要表单id和字段
    def queryall(self,formid,fields,filterstring=''):
        result=[]
        firstrow=0
        page = self.kquery(formid,fields, firstrow,filterstring)    
        result += page
        while(len(page)==100):
            firstrow+=100
            page = self.kquery(formid,fields,firstrow,filterstring)
            result += page
        return result
    
    #通过名称获得编号
    def getFnumberByName(self,formid,fname):

        namefield = 'fname'
        if formid == 'BOS_ASSISTANTDATA_DETAIL':
            namefield='fdatavalue'
        req={
        "FormId": formid,
        "FieldKeys": 'fnumber',
        "FilterString": "{}='{}'".format(namefield,fname),
        }
        res = self.api.ExecuteBillQuery(req)
        res = json.loads(res)
        if len(res)>0:
            return res[0][0]
        return None

    #金蝶创建客户,需要编号和客户名称
    def savecu(self,fnumber,fname):
        '''
        保存客户的方法
        '''
        req={
            "NeedUpDateFields": [],
            "NeedReturnFields": [],
            "IsDeleteEntry": "true",
            "SubSystemId": "",
            "IsVerifyBaseDataField": "false",
            "IsEntryBatchFill": "true",
            "ValidateFlag": "true",
            "NumberSearch": "true",
            "InterationFlags": "",
            "Model": {
                "FNumber": fnumber,
                "FCreateOrgId": {
                    "FId": "1"
                },
                "FUseOrgId": {
                    "FId": "1"
                },
                "FName": fname,
                "FINVOICETITLE": fname,
                "FTRADINGCURRID": {
                    "FNumber": "PRE001"
                }
                
            }
        }
        res = self.api.Save(customer_mod,req)
        return json.loads(res)
    
        #创建\分配\提交\审核客户一体化方法
    def customer_create(self,fname,orgs=''):
        '''
        orgs可以不填
        '''
        if orgs =='':
            orgs=self.GetOrgIds()
        finalresult={}
        formid='BD_Customer'
        cu_query_fields='FNUMBER,Fname,FCUSTID,FCreateOrgId,Fuseorgid'
        res_query = self.queryall(formid,cu_query_fields)
        if len(res_query)>0:
            lastfnumber =res_query[len(res_query)-1][0]
        else:
            lastfnumber='00000'
        fnumber = str(int(lastfnumber)+1).zfill(5)
        res_save=self.savecu(fnumber,fname)
        finalresult['res_save']=res_save
        id=res_save['Result']['Id']
        res_alocate =self.api.Allocate(formid,{'Pkids':id,'TOrgIds':orgs}) 
        req_sub_auid={'Numbers':[fnumber]}
        finalresult['res_alocate']=res_alocate
        res_sub=self.api.Submit('BD_Customer',req_sub_auid)
        finalresult['res_sub']=res_sub
        res_audit = self.api.Audit('BD_Customer',req_sub_auid)        
        finalresult['res_audit']=res_audit
        return finalresult

    def GetOrgIds(self):
        orgs = self.kquery('ORG_Organizations','fname,forgid')
        orgids=''
        for org in orgs:
            if org[1]==1:continue
            if orgids=='':
                orgids+=str(org[1])
            else:
                orgids+=',{}'.format(org[1])
        return orgids
