import pytz
import requests
import random
import cv2
from urllib.parse import quote
import re
import io
import json
import time
import numpy as np
import ddddocr
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta

import config
# 请求头部分
session = requests.session()

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'cas.sysu.edu.cn',
    'Origin': 'https://cas.sysu.edu.cn',
    'Pragma': 'no-cache',
    'Referer': 'https://cas.sysu.edu.cn/cas/login',
    'Sec-CH-UA': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'Sec-CH-UA-Mobile': '?0',
    'Sec-CH-UA-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

headers1 = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "gym.sysu.edu.cn",
    "Pragma": "no-cache",
    "Sec-CH-UA": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
}

headers2 = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Host": "gym.sysu.edu.cn",
    "Origin": "https://gym.sysu.edu.cn",
    "Pragma": "no-cache",
    "Referer": "https://gym.sysu.edu.cn/",
    "Sec-CH-UA": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}


def log(netiedid, password):
    # selenium.webdriver 模拟登录获取Cookies和Authorization部分
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    chrome_driver_path = '../chromedriver-win32/chromedriver.exe'
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # 访问登录页面
    driver.get("https://cas.sysu.edu.cn/cas/")
    driver.maximize_window()
    driver.implicitly_wait(2 + random.random() * 6.6)
    username_input = driver.find_element(By.XPATH, "//input[@id='username']")
    username_input.send_keys(netiedid)
    password_input = driver.find_element(By.XPATH, "//input[@id='password']")
    password_input.send_keys(password)

    captcha_img = driver.find_element(By.XPATH, "//img[@id='captchaImg']")
    location = captcha_img.location
    size = captcha_img.size
    driver.save_screenshot(f'./vertify_pic/page_screenshot_{netiedid}.png')
    img = Image.open(f'./vertify_pic/page_screenshot_{netiedid}.png')
    left = 2 * location['x']
    top = 2 * location['y']
    right = 2 * (location['x'] + size['width'])
    bottom = 2 * (location['y'] + size['height'])
    captcha_img_screenshot = img.crop((left, top, right, bottom))
    captcha_img_screenshot.save(f'./vertify_pic/orignal_vertify_code_{netiedid}.jpg')

    img = Image.open(f'./vertify_pic/orignal_vertify_code_{netiedid}.jpg')
    ## 验证码图片处理
    width = img.size[0]  # 长度
    height = img.size[1]  # 宽度
    for i in range(0, width):  # 遍历所有长度的点
        for j in range(0, height):  # 遍历所有宽度的点
            data = (img.getpixel((i, j)))  # 打印该图片的所有点
            if (data[0] <= 25 and data[1] <= 25 and data[2] <= 25):  # RGBA的r,g,b均小于25
                img.putpixel((i, j), (255, 255, 255, 255))  # 则这些像素点的颜色改成白色
    img = img.convert("RGB")  # 把图片强制转成RGB片
    img = np.array(img)
    grayimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(grayimg, 160, 255, cv2.THRESH_BINARY)
    img = Image.fromarray(thresh)

    ## 验证码识别
    ocr1 = ddddocr.DdddOcr()
    ocr2 = ddddocr.DdddOcr(beta=True)
    img.save(f'./vertify_pic/grayimg-vertify_code_{netiedid}.jpg')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    bytes_like_object = buffer.getvalue()
    verification1 = ocr1.classification(bytes_like_object)
    verification2 = ocr2.classification(bytes_like_object)

    print(verification1, verification2)
    if verification1 == verification2:
        verification = verification1
    else:
        return False

    captcha_input = driver.find_element(By.XPATH, "//input[@id='captcha']")
    captcha_input.send_keys(verification)
    login_button = driver.find_element(By.XPATH, "//input[@name='submit']")
    login_button.click()

    driver.implicitly_wait(2 + random.random() * 6.6)
    driver.get("https://gym.sysu.edu.cn/index.html")
    driver.implicitly_wait(2 + random.random() * 6.6)

    Authorization = driver.execute_script("return localStorage.getItem('scientia-session-authorization');")
    Authorization_data = json.loads(Authorization)
    token = Authorization_data['access_token']
    print(f"token:{token}")
    headers["Authorization"] = f"Bearer {token}"
    headers1["Authorization"] = f"Bearer {token}"
    headers2["Authorization"] = f"Bearer {token}"

    cookies = driver.get_cookies()
    cookie = cookies[0]
    cookie_value = cookie['value']
    print(f"cookie:{cookie_value}")
    headers["Cookie"] = cookie_value
    headers1["Cookie"] = cookie_value
    headers2["Cookie"] = cookie_value

    driver.implicitly_wait(2 + random.random() * 6.6)
    driver.close()
    return True


def get_field_info(VenueTypeId, target_date, target_starttime, fields_order):
    # 获取场地信息部分
    ## 打印登录账号信息
    info_url = "https://gym.sysu.edu.cn/api/Credit/Me"
    resinfo = session.get(info_url, headers=headers1)
    # print(resinfo.text)


    start_date = str(datetime.now().date())
    end_date = str(datetime.now().date() + timedelta(days=3))

    ## 获取场地信息
    venid_url = ("https://gym.sysu.edu.cn/api/venue/available-slots/range?venueTypeId=" + VenueTypeId
                 + "&start=" + start_date + "&end=" + end_date)
    ressearch = session.get(venid_url, headers=headers1)
    ressearch_json = ressearch.json()

    expected_list = []
    for item in ressearch_json:
        if ("场地16" not in item["VenueName"]) and ("场地17" not in item["VenueName"])\
                and ("场地11" not in item["VenueName"]) and ("场地15" not in item["VenueName"])\
                and ("场地10" not in item["VenueName"]):
            slot_list = []
            for timeslot in item['Timeslots']:
                if (timeslot['Date'] == target_date and timeslot['Start'] in target_starttime
                        and timeslot['AvailableCapacity'] == 5):
                    del timeslot["AvailableCapacity"]
                    slot_list.append(timeslot)
            if slot_list:
                expected_list.append((item["VenueId"], item["VenueName"], slot_list))

    order_map = {venue: index for index, venue in enumerate(fields_order)}
    expected_list = sorted(expected_list, key=lambda x: order_map.get(next(filter(lambda v: v in x[1], fields_order), None), float("inf")))


    VenueBookings = [{"VenueId": VenueId, "VenueName": VenueName, "TimeSlots": slot_list}
                 for (VenueId, VenueName, slot_list) in expected_list]
    return VenueBookings



def generate_uuid():
    def replace(match):
        e = match.group(0)
        t = random.randint(0, 15)
        a = t if e == 'x' else (t & 0x3 | 0x8)
        return f"{a:x}"
    template = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
    uuid = re.sub(r'[xy]', replace, template)
    return uuid


def book(VenueTypeId, VenueBookings, charge, netiedid):
    # 锁定场地部分
    created_at = datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
    book_data = {
        "Identity": generate_uuid(),
        "BookingId": generate_uuid(),
        "VenueTypeId": VenueTypeId,
        "VenueBookings": VenueBookings,
        "Participants": [],
        "Status": "Accepted",
        "Description": "南校园新体育馆羽毛球场（学生）",
        "CreatedAt": created_at,
        "UpdatedAt": created_at,
        "ActionedBy": netiedid,
        "IsCash": False,
        "Charge": charge,
        }
    print(book_data)
    book_url = "https://gym.sysu.edu.cn/api/BookingRequestVenue"
    resbook = session.post(book_url, headers=headers2, json=book_data)
    print(resbook.text)
    if resbook.json().get("Code") == 200:
        return "成功预约"
    elif resbook.json().get("Code") == 400 and ("您每天最多可以预约2个时间段" in resbook.json().get("Result")):
        print(resbook.json())
        return "您每天最多可以预约2个时间段"
    return "其他情况"



def time_transform(utc_time_str):
    utc_dt = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc)
    local_dt = utc_dt.astimezone(pytz.timezone('Asia/Shanghai'))
    formatted_time = local_dt.strftime('%Y-%m-%d %H:%M') + '-' + (local_dt + timedelta(hours=1)).strftime('%H:%M')
    return formatted_time


def invite(participants, VenueBookings):
    # 发送邀请部分
    paticipants_list = []
    for participant in participants:
        encoded_participant = quote(participant)
        filter_url = ("https://gym.sysu.edu.cn/api/Credit/Find?Page=1&PageSize=10&SearchFilter="
                      + encoded_participant + "&TypeFilter=&WalletId=SPORT")
        resfilter = session.get(filter_url, headers=headers2)
        filter_json = resfilter.json()
        paticipants_list.append(filter_json["Items"][0])
        # print(filter_json["Items"][0])

    print(f"被邀请对象:{[(item['Name'], item['HostKey'], item['UserId']) for item in paticipants_list]}")

    # 获取订单信息
    today = datetime.today()
    days_before = today - timedelta(days=5)
    days_later = today + timedelta(days=5)
    order_url = "https://gym.sysu.edu.cn/api/BookingRequestVenue"
    order_params = {
        "all": "false",
        "startDate": days_before.strftime("%Y-%m-%d"),
        "endDate": days_later.strftime("%Y-%m-%d"),
        "waitingList": "false"
    }
    resorder = requests.get(order_url, params=order_params, headers=headers2)
    order_json = resorder.json()

    url_Identity = []
    venue_id_name = [(booking["VenueId"], booking["VenueName"]) for booking in VenueBookings]
    VenueId, VenueName = [item[0] for item in venue_id_name], [item[1] for item in venue_id_name]
    for item in order_json:
        if item["VenueId"] in VenueId and item['VenueName'] in VenueName and item["Status"] == "Accepted"\
                and str(datetime.strptime(item["StartDateTime"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")) == config.target_date:
            url_Identity.append((item["Identity"], item["VenueName"], item["StartDateTime"]))

    # 发送邀请
    for Identity in url_Identity:
        invent_url = ("https://gym.sysu.edu.cn/api/BookingRequestVenue/"
                      + Identity[0] + "/Participants")
        invent_data = []
        for item in paticipants_list:
            invent_data.append({
                "UserId": item["UserId"],
                "Name": item["Name"] + " " + "(" + item["HostKey"] + ")",
                "HostKey": item["HostKey"],
                "Status": "Pending"
            })
        resinvite = session.post(invent_url, headers=headers2, json=invent_data)

        if resinvite.status_code == 204:
            print(f"{Identity[1],time_transform(Identity[2])}发送邀请成功")
            time.sleep(random.random() * 8.88)
        else:
            print(f"{Identity[1],time_transform(Identity[2])}发送邀请失败，状态码：{resinvite.status_code}")


def check_order(VenueBookings):
    # 检查订单状态，接受邀请是否成功
    today = datetime.today()
    days_before = today - timedelta(days=5)
    days_later = today + timedelta(days=5)
    order_url = "https://gym.sysu.edu.cn/api/BookingRequestVenue"
    order_params = {
        "all": "false",
        "startDate": days_before.strftime("%Y-%m-%d"),
        "endDate": days_later.strftime("%Y-%m-%d"),
        "waitingList": "false"
    }
    resorder = requests.get(order_url, params=order_params, headers=headers2)
    order_json = resorder.json()

    venue_id_name = [(booking["VenueId"], booking["VenueName"]) for booking in VenueBookings]
    VenueId, VenueName = [item[0] for item in venue_id_name], [item[1] for item in venue_id_name]
    for item in order_json:
        if ((item["VenueId"] in VenueId) and (item['VenueName'] in VenueName)
                and item["Status"] == "Accepted"):
            # 存在邀请人时要多加一个判定条件 and item["Participants"][0]['Status'] == "Accepted"
            # print(f"已接受邀请，预定成功:{item['VenueName'], time_transform(item['StartDateTime'])}")
            print(f"预定成功:{item['VenueName'], time_transform(item['StartDateTime'])}")

