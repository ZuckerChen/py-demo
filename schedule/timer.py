# 误删进程，有疑问请联系chenzhang@nonobank.com
import datetime
import json
import urllib.error
import urllib.request
from threading import Timer
import pymysql

interval = 60 * 10


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def nowIntervalSec(seconds):
    return (datetime.datetime.now() + datetime.timedelta(seconds=seconds)).strftime("%Y-%m-%d %H:%M:%S")


# 发送解锁请求
def post_json(url, headers, values):
    try:
        jsonData = json.dumps(values)
        data = bytes(jsonData, 'utf8')
        request = urllib.request.Request(url, headers=headers)
        page = urllib.request.urlopen(request, data).read()
        page = page.decode('utf-8')
        target = json.loads(page)
    except Exception as e:
        print("出错了妈蛋{0}".format(e))
    else:
        pass
    return target


# 取数据库
def getData():
    db = pymysql.connect("172.16.0.101", "dev", "beX5kFn4", "db_nono_pay", charset='utf8')
    cursor = db.cursor()
    sql = "SELECT order_no FROM db_nono_pay.tb_p2p_retry WHERE  status ='WARN' and remark like '%CE999053%'"
    cursor.execute(sql)
    data = cursor.fetchall()
    db.close()
    cursor.close()
    return data;


# 自调任务
def task():
    print("定时任务开始执行 time:" + now())
    data = getData()
    dealLst = []
    if len(data) > 0:
        for iterm in data:
            dealLst.append(iterm[0])
        print("开始批量解锁...")
        print(dealLst)
        url = "http://pay.prod.com/pay-app/v1/p2p/repair/withdrawCancel"
        headers = {}
        values = {"ids": dealLst}
        headers['Content-Type'] = 'application/json; charset=utf-8'
        target = post_json(url, headers, values)
        print(target)
        print("批量解锁完毕...")

    if (len(data) == 0):
        print("无需要解锁数据")
    print("定时任务执行完成，下次执行时间 time:" + nowIntervalSec(interval))
    Timer(interval, task).start()


print("@@@@@@@@@@@@@@@@@@@@@")
print("Let's Go!")
print("@@@@@@@@@@@@@@@@@@@@@")
Timer(interval, task).start()
