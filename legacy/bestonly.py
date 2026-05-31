import requests
from bs4 import BeautifulSoup
import random
import cv2
import logging
import sys
from email.mime.text import MIMEText
import smtplib
import io
import json
import numpy as np
import ddddocr
from lxml import etree
from PIL import Image
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_MISSED, EVENT_JOB_EXECUTED
import config

session = requests.session()

# 普通请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


# 能处理Ajax的请求头
headers1 = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host': 'gym.sysu.edu.cn',
    'Origin': 'https://gym.sysu.edu.cn',
    'Referer': 'https://gym.sysu.edu.cn/pay/show.html?id=1729668048295462',
    'Sec-CH-UA': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
    'Sec-CH-UA-Mobile': '?0',
    'Sec-CH-UA-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
}


# 日志配置
logging.basicConfig(filename='bestonly.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8', filemode='w')


class Logger(object):
    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message.rstrip() != '':  # 检查消息是否为空
            logging.log(self.level, message.rstrip())

    def flush(self):
        pass


# 将标准输出和标准错误重定向到日志
sys.stdout = Logger(logging.INFO)
sys.stderr = Logger(logging.ERROR)


# 登录
def login(netiedid, password):
    print(netiedid, password)
    login_url = "https://cas.sysu.edu.cn/cas/login?service=https%3A%2F%2Fgym.sysu.edu.cn%2Flogin%2Fpre.html"
    html = session.post(login_url, headers=headers).text
    soup = BeautifulSoup(html, 'lxml')
    execution = soup.find('input', {'name': 'execution'})['value']
    _eventId = soup.find('input', {'name': '_eventId'})['value']
    btn = soup.find('input', {'name': 'submit'})['value']

    response = requests.get(login_url)
    time.sleep(random.random() * 0.31415926 + 0.271828359)
    tree = etree.HTML(response.content)
    img_url = tree.xpath('//img[@id="captchaImg"]/@src')[0]
    # 保存并识别验证码
    img = session.get(url="https://cas.sysu.edu.cn/cas/" + img_url, headers=headers).content
    with open('./vertify_pic/orignal_vertify_code.jpg', 'wb') as file:
        file.write(img)
    img = Image.open('./vertify_pic/orignal_vertify_code.jpg')

    # 验证码图片处理
    width = img.size[0]  # 长度
    height = img.size[1]  # 宽度
    for i in range(0, width):  # 遍历所有长度的点
        for j in range(0, height):  # 遍历所有宽度的点
            data = (img.getpixel((i, j)))  # 打印该图片的所有点
            if (data[0] <= 25 and data[1] <= 25 and data[2] <= 25):  # RGBA的r,g,b均小于25
                img.putpixel((i, j), (255, 255, 255, 255))  # 则这些像素点的颜色改成白色
    img = img.convert("RGB")  # 把图片强制转成RGB片
    # 灰度化
    img = np.array(img)
    grayimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(grayimg, 160, 255, cv2.THRESH_BINARY)
    img = Image.fromarray(thresh)
    # 验证码识别
    ocr1 = ddddocr.DdddOcr(old=True)
    ocr2 = ddddocr.DdddOcr(old=False)
    img.save('./vertify_pic/grayimg-vertify_code.jpg')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    bytes_like_object = buffer.getvalue()
    verification1 = ocr1.classification(bytes_like_object)
    verification2 = ocr2.classification(bytes_like_object)
    # 两种识别方法相互验证
    if verification1 != verification2:
        return False
    verification = verification1
    print('识别的验证码：' + verification)

    login_data = {
        'username': netiedid,
        'password': password,
        'captcha': verification,
        'execution': execution,
        '_eventId': _eventId,
        "btn btn - submit btn - block": btn
    }
    res = session.post(url=login_url, headers=headers, data=login_data, allow_redirects=True)

    url = "https://gym.sysu.edu.cn/product/show.html?id=" + config.s
    html = session.post(url, headers=headers).text
    soup = BeautifulSoup(html, 'lxml')
    onlinename = soup.find('input', {"id": "onlinename"})['value']
    print(f"订场人姓名：", onlinename)

    if onlinename:
        print('登陆成功，状态码：', res.status_code, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return True
    else:
        print('登陆失败，状态码：', res.status_code, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return False


# 发送邮件通知
def send_email(title, message, receiver):
    sender = config.sender
    smtpserver = config.smtpserver
    username = config.username
    password_email = config.password_email

    msg = MIMEText(message, 'html', 'utf-8')
    msg['Subject'] = title
    msg['from'] = sender
    msg['to'] = receiver
    smtp = smtplib.SMTP_SSL(smtpserver, 465)  # 加密方式
    smtp.esmtp_features["auth"] = "PLAIN"
    (code, resp) = smtp.login(username, password_email)
    if code == 0:
        print("mail fail"+"\t" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    else:
        print("mail success"+"\t" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        resultm = smtp.sendmail(sender, receiver, msg.as_string())
        print(resultm)
        smtp.quit()
    pass


# 预定
def pay():
    weekday = datetime.strptime(config.bookdate, "%Y-%m-%d").weekday()
    wday = config.weekd[weekday]

    order_id = ""
    while True:
        if not order_id:
            try:
                urlo = "https://gym.sysu.edu.cn/order/seachData.html"
                search = {
                    "orderid": "",
                    "id": "",
                    "page": 1,
                    "rows": 10
                }
                reso = session.post(urlo, data=search, headers=headers)
                print("订单信息获取：" + str(reso.status_code))
                resulto = reso.json()

                w = None
                for item in resulto.get('rows'):
                    if item.get('orderid'):
                        w = item
                        break

                date_time = datetime.strptime(w.get("order").get('createdate'), "%Y-%m-%d %H:%M:%S")
                date_book = date_time.date()
                current_date = datetime.now().date()
                print("第一个订单下单时间：" + str(date_time))

                if str(current_date) == str(date_book):
                    print("第一个订单编号：" + w.get('orderid'))
                    order_id = w.get('orderid')

                else:
                    print("未抢到场地")
                    time.sleep(random.random() * 0.31415926 + 0.271828359)
                    return False

            except:
                print("error")
                time.sleep(random.random() * 0.31415926 + 0.271828359)
                return False


        elif order_id:
            print("正在支付,orderid=" + order_id)
            trytimes = 1
            n = 3
            while trytimes:
                try:
                    if trytimes % n == 0:
                        urlo = "https://gym.sysu.edu.cn/order/seachData.html"
                        search = {
                            "orderid": "",
                            "id": "",
                            "page": 1,
                            "rows": 10
                        }
                        reso = session.post(urlo, data=search, headers=headers)
                        resulto = reso.json()
                        for item in resulto.get('rows'):
                            if order_id == item.get('orderid') and item.get('status') == 1:

                                playtime0 = item.get('stock').get("time_no")
                                field0 = item.get('stockdetail').get("sname")
                                print("支付成功" + "\t" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                                print("订场成功:" + config.bookdate + wday + "\t" + playtime0 + field0)
                                send_email("自动订场成功",
                                           f"{config.bookdate}\n{wday}\n{playtime0}\n{field0}",
                                           config.receiver[0])
                                print("预定完成" + "\t" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                                trytimes = 0
                                return True

                    print(f"订单编号:" + str(order_id))
                    url2 = "https://gym.sysu.edu.cn/pay/show.html?id=" + order_id
                    print('去支付的网址(失败也会锁定场地，可以自己支付)：', url2)

                    # 提取支付信息
                    html2 = session.post(url=url2, headers=headers).text
                    time.sleep(random.random() * 3.1415926 + 2.71828359)
                    soup = BeautifulSoup(html2, 'lxml')
                    item = soup.find('li', class_='bankitem selected')
                    payif = item.get('data-val')
                    payid = item.get('data-payid')
                    print(f"支付信息：", payif + "\t" + payid)

                    # 预验证支付信息
                    url3 = ("https://gym.sysu.edu.cn/pay/" + payif + "/showpay.html"
                            + "?orderid=" + order_id + "&payid=" + payid + "&json=html&_=" + str(
                                time.time() * 1000))
                    payment = {
                        'orderid': order_id,
                        'payid': payid,
                    }
                    session.get(url3, data=payment, headers=headers1)

                    # 支付
                    payload = {
                        'payid': payid,
                        'orderid': order_id,
                        "ctypeindex": "0"
                    }
                    payload_json = json.dumps(payload)
                    urls = "https://gym.sysu.edu.cn/pay/" + payif + "/topay.html"
                    ress = session.post(urls, data={'param': payload_json}, headers=headers1)

                    result0 = ress.json()
                    print(result0)
                    if result0.get('result') == '1':
                        print("支付成功,正在查看订单并发送邮件" + "\t" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        trytimes = n
                    else:
                        trytimes += 1
                        print("支付失败" + "\t" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                              result0.get('message'))
                        time.sleep(8.88 * random.random() * 3.1415926 + 2.71828359)
                except:
                    print("已锁场，支付失败，重新支付中" + "\t" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    trytimes += 1
                    time.sleep(8.88 * random.random() * 3.1415926 + 2.71828359)


def find():
    param = {
        "s_date": config.bookdate,
        "serviceid": config.s,
        "_": str(time.time() * 1000),
    }

    url = ("https://gym.sysu.edu.cn/product/findOkArea.html?"+"s_date="
           + str(config.bookdate)+"&serviceid="+config.s+"&_="+str(time.time() * 1000))
    resf = session.get(url, data=param, headers=headers1)
    result = resf.json()
    resultf = result.get('object')
    if resultf:
        return resultf
    else:
        return None


def book():
    print("程序开始："+"\t" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    netiedid = config.best_netiedid
    password = config.best_password

    loginsucess = False
    reserve = True
    while True:
        if datetime.now().hour == 0 and datetime.now().minute >= 36:
            break

        if not reserve:
            break
        # 登陆
        t = 0
        while not loginsucess:
            t += 1
            if t > 5:
                break
            try:
                print("正在登录" + "\t" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                if login(netiedid, password):
                    loginsucess = True
                    print('登陆成功' + "\t" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    time.sleep(random.random() * 31.415926 + 2.71828359)
                    print("登录失败" + "\t" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            except:
                time.sleep(random.random() * 31.415926 + 2.71828359)
                continue

        if not loginsucess:
            print("登陆失败，重新启动任务")
            scheduler.remove_job(job.id)
            scheduler.reschedule_job(job.id, trigger='date', run_date=datetime.now(), misfire_grace_time=600)
            break

        resultf = None
        while not resultf:
            try:
                resultf = find()
                resultf = [item for item in resultf if (item.get('status') == 1)
                           and (item.get('stock').get('time_no') in config.best_playtimes)
                           and (item.get('sname') in config.best_fields)]
                if resultf:
                    print("有场地剩余,正在跳转订场"+"\t" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                    # 排序
                    time_dict = {t: i for i, t in enumerate(config.best_playtimes)}
                    play_dict = {p: i for i, p in enumerate(config.best_fields)}

                    resultf = sorted(resultf, key=lambda x: (
                        time_dict.get(x.get('stock').get('time_no'), float('inf')),
                        play_dict.get(x.get('sname'), float('inf'))))

                    for item in resultf:
                        print(item.get('stock').get('time_no') + "\t" + item.get('sname'))
                else:
                    time.sleep(random.random() * 0.31415926 + 0.271828359)
                    break
            except:
                time.sleep(random.random() * 0.31415926 + 0.271828359)
                continue

        while datetime.now().hour != 0:
            time.sleep(random.random())

        booksuccess = False
        while resultf:
            if booksuccess:
                break

            for item in resultf:
                stockid = item.get('stockid')
                datadid = item.get('id')
                datadid = str(datadid)
                stockid = str(stockid)

                playtime = item.get('stock').get('time_no')
                field = item.get('sname')

                print("正在预定" + "\t" + config.bookdate + "\t" + playtime + "\t" + field)

                try:
                    print("尝试预定中" + "\t" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                    param1 = {
                        "activityPrice": 0,
                        "activityStr": None,
                        "address": None,
                        "dates": None,
                        "extend": None,
                        "flag": "0",
                        "isBulkBooking": None,
                        "isbookall": "0",
                        "isfreeman": "0",
                        "istimes": "1",
                        "mercacc": None,
                        "merccode": None,
                        "order": None,
                        "orderfrom": None,
                        "remark": None,
                        "serviceid": None,
                        "shoppingcart": "0",
                        "sno": None,
                        "stock": {stockid: "1"},
                        "stockdetail": {stockid: datadid},
                        "stockdetailids": datadid,
                        "stockid": None,
                        "subscriber": "0",
                        "time_detailnames": None,
                        "userBean": None
                    }
                    param1_json = json.dumps(param1)
                    url1 = 'https://gym.sysu.edu.cn/order/book.html'
                    res1 = session.post(url=url1, data={'param': param1_json}, headers=headers)
                    resj = res1.json()
                    print(resj)
                    if resj.get('result') == "2":
                        print("成功确认场地" + "\t" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        booksuccess = True
                        break
                    elif "预订数量超过限制" in resj.get('message'):
                        print("已锁定场地" + "\t" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        booksuccess = True
                        break
                    elif "座位已被预订" in resj.get('message'):
                        print(playtime + "\t" + field + "\t" + "已被预定")
                        del resultf[item]
                    elif "数据有误，请重新预订" in resj.get('message'):
                        print(playtime + "\t" + field + "\t" + "数据有误")
                        time.sleep(8.88 * random.random())

                    time.sleep(random.random() * 0.31415926 + 0.271828359)

                except:
                    time.sleep(random.random() * 0.31415926 + 0.271828359)
                    continue

        if pay():
            scheduler.shutdown()
            print("Scheduler stopped.")
            break

        else:
            print("预定失败" + "\t" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            time.sleep(random.random() * 0.31415926 + 0.271828359)
            scheduler.shutdown()
            print("Scheduler stopped.")
            break


# 定义任务监听器
def job_listener(event):
    # 检查是否是任务错过事件
    if event.code == EVENT_JOB_MISSED:
        print(f"任务 {event.job_id} 错过了执行，正在重新调度...")
        # 重新调度错过的任务
        scheduler.reschedule_job(event.job_id, trigger='date', run_date=datetime.now(), misfire_grace_time=600)


if __name__ == "__main__":
    # 增加线程池大小为10
    scheduler = BlockingScheduler(executors={'default': ThreadPoolExecutor(max_workers=10)})

    if datetime.now().hour >= 22:
        start_date = datetime.now().replace(
            hour=23, minute=50 + int(6 * random.random()), second=int(60 * random.random()))
        job = scheduler.add_job(book, 'date', run_date=start_date, misfire_grace_time=600)
    else:
        run_date = datetime.now() + timedelta(seconds=1)
        job = scheduler.add_job(book, 'date', run_date=run_date, misfire_grace_time=600)

    # 添加任务监听器，监听任务错过和执行完成事件
    scheduler.add_listener(job_listener, EVENT_JOB_MISSED | EVENT_JOB_EXECUTED)

    # 启动调度器
    scheduler.start()
