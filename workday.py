from greg_pkg.elkhelper import elkhelper
import os
import datetime
user=os.environ['esid']
pw=os.environ['espw']
esadd=os.environ['esadd']
elk=elkhelper(esadd,(user,pw))

predata={
    #法定节假日
    "holiday":[
        #元旦节
        "2023-01-01",
        "2023-01-02",
        #春节
        "2023-01-21",
        "2023-01-22",
        "2023-01-23",
        "2023-01-24",
        "2023-01-25",
        "2023-01-26",
        "2023-01-27",
        #清明节
        "2023-04-05",
        #劳动节
        "2023-04-29",
        "2023-04-30",
        "2023-05-01",
        "2023-05-02",
        "2023-05-03",
        #端午节
        "2023-06-22",
        "2023-06-23",
        "2023-06-24",
        #中秋节+国庆节
        "2023-09-29",
        "2023-09-30",
        "2023-10-01",
        "2023-10-02",
        "2023-10-03",
        "2023-10-04",
        "2023-10-05",
        "2023-10-06"
    ],
    #补休
    "annoyday":[
        #春节
        "2023-01-28",
        "2023-01-29",
        #端午节
        "2023-04-23",
        #劳动节
        "2023-05-06",
        #端午节
        "2023-06-25",
        #中秋节+国庆节
        "2023-10-07",
        "2023-10-08"
    ]
}

def dataReady(predata):
    def isHolidy(date):
        if date.isoformat() in predata["holiday"]:
            return True
        if date.isoformat() in predata["annoyday"]:
            return False
        if date.isoweekday() in [6,7]:
            return True
        return False
    start = datetime.date(2023,1,1)
    start = predata['holiday'][0]
    start = datetime.date.fromisoformat(start)
    current = start
    req=[]
    while current.year==start.year:
        dtstr = current.isoformat()
        obj={
            "date":dtstr
            ,"id":dtstr.replace("-","")
            ,"is_holidy":isHolidy(current)        
            ,"is_weekend":current.isoweekday() in [6,7]
            ,"month":current.month
            ,"year":current.year
            ,"day":current.day
        }
        req.append(obj)
        current+=datetime.timedelta(days=1)    
    res = elk.bulk("annoycalendar",req)
    try:
        print(f"更新数据库，故障：{res['errors']}")
    except:
        print(f"更新数据库，异常：{res}")           
dataReady(predata)



res = elk.getAllData("annoycalendar")
DateStore = {x['date']:x for x in res}
def workDayCac(start:str,end:str,includeStartDay=True):
    firstday=True
    count=0
    try:
        start = datetime.date.fromisoformat(start)
        end = datetime.date.fromisoformat(end)        
        while start<=end:
            cData =DateStore[str(start)] 
            if firstday:
                if not (cData['is_holidy']):
                    if includeStartDay:
                        count+=1
                firstday=False
            else:                
                if not (cData['is_holidy']):count+=1
            start +=datetime.timedelta(days=1)
        return count 
    except Exception as ex:
        print(f"异常:{ex}")

total=0
for i in range(1,13):
    s = datetime.date(2023,i,1)
    e = s+datetime.timedelta(days=31)
    while(e.month!=s.month):
        e-=datetime.timedelta(days=1)
    count = workDayCac(str(s),str(e))
    total+=count
    print(f"{i}月一共有{count}个工作日")
print(f"总计有{total}个工作日")