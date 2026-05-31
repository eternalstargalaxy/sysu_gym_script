import pytz
import requests
import random
import cv2
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

def log(participant_netiedid, participant_password):
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
    username_input.send_keys(participant_netiedid)
    password_input = driver.find_element(By.XPATH, "//input[@id='password']")
    password_input.send_keys(participant_password)

    captcha_img = driver.find_element(By.XPATH, "//img[@id='captchaImg']")
    location = captcha_img.location
    size = captcha_img.size
    driver.save_screenshot('./vertify_pic/page_screenshot_receive.png')
    img = Image.open('./vertify_pic/page_screenshot_receive.png')
    left = 2 * location['x']
    top = 2 * location['y']
    right = 2 * (location['x'] + size['width'])
    bottom = 2 * (location['y'] + size['height'])
    captcha_img_screenshot = img.crop((left, top, right, bottom))
    captcha_img_screenshot.save('./vertify_pic/orignal_vertify_code_receive.jpg')

    img = Image.open('./vertify_pic/orignal_vertify_code_receive.jpg')
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
    img.save('./vertify_pic/grayimg-vertify_code_receive.jpg')
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



def time_transform(utc_time_str):
    utc_dt = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc)
    local_dt = utc_dt.astimezone(pytz.timezone('Asia/Shanghai'))
    formatted_time = local_dt.strftime('%Y-%m-%d %H:%M') + '-' + (local_dt + timedelta(hours=1)).strftime('%H:%M')
    return formatted_time


# 接受邀请部分
def receive():
    # 打印登录账号信息
    info_url = "https://gym.sysu.edu.cn/api/Credit/Me"
    resinfo = session.get(info_url, headers=headers1)
    print(resinfo.text)

    # 查询被邀请订单
    Participants_url = "https://gym.sysu.edu.cn/api/BookingRequestVenue/Participants"
    resparticipants = session.get(Participants_url, headers=headers2)
    resparticipants_json = resparticipants.json()

    # 读取最近两条被邀请记录
    Identity_list = []
    for item in resparticipants_json[-2:]:
        Identity_list.append((item["Identity"], item["VenueName"], item["StartDateTime"]))

    for item in Identity_list:
        accept_url = f"https://gym.sysu.edu.cn/api/BookingRequestVenue/{item[0]}/Participants/Accept"
        resaccept = requests.post(accept_url, headers=headers2, json=None)

        if resaccept.status_code == 204:
            print(f"{item[1],time_transform(item[2])}接受邀请成功")
            time.sleep(random.random() * 8.88)
        else:
            print(f"{item[1],time_transform(item[2])}接受邀请失败，状态码：{resaccept.status_code}")

