import logging
import sys
import time
import random
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_MISSED, EVENT_JOB_EXECUTED
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import smtplib


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


import book_invite
import config
import receive

def main():
    # 日志配置
    logging.basicConfig(filename=f'main.log', level=logging.INFO,
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


    # 登录主账号
    netiedid, password = config.netiedid, config.password

    # 邀请人信息
    # participant_netiedid, participant_password = config.participant_netiedid, config.participant_password

    while True:
        try:
            if book_invite.log(netiedid, password):
                break
            else:
                time.sleep(8.88 + random.random()*36)
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(8.88 + random.random()*36)
            continue
    print("主账号登陆成功")

    if config.way == "scheduled":
        # 等待22：00
        while datetime.now().hour != 22:
            if datetime.now().hour == 21 and datetime.now().minute >= 58:
                time.sleep(random.random() * 0.66)
            else:
                time.sleep(60)
    elif config.way == "directly":
        pass


    venuebooking = None

    # 循环获取场地信息 + 订场
    success = False
    while True:
        try:
            VenueBookings = (book_invite.get_field_info
                             (config.VenueTypeId, config.target_date, config.target_starttime, config.fields_order))
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(random.random() * 0.66)
            continue


        for VenueBooking in VenueBookings:
            try:
                result = book_invite.book(config.VenueTypeId, [VenueBooking], config.charge, netiedid)
                if result == "成功预约":
                    venuebooking = [VenueBooking]
                    print(f"订场成功{venuebooking}")
                    success = True
                    break
                elif result == "您每天最多可以预约2个时间段":
                        print("已存在订单，每天最多可以预约2个时间段")
                        success = True
                        break


            except Exception as e:
                print(f"An error occurred: {e}")
                time.sleep(random.random() * 0.66)
                continue
        if success:
            break

    """
    # 循环发送邀请
    while True:
        try:
            book_invite.invite(config.participants, venuebooking)
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(random.random() * 0.66)
            continue

    # 循环接受邀请
    while True:
        try:
            if receive.log(participant_netiedid, participant_password):
                print("接受邀请账号登陆成功")
                break
            else:
                time.sleep(8.88 + random.random() * 36)
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(8.88 + random.random() * 36)
            continue

    while True:
        try:
            receive.receive()
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(random.random() * 0.66)
            continue
    """

    if not venuebooking:
        print("当日已存在两个场地订单，请自行查看场地信息")
        if config.mail:
            send_email("自动订场完成",
                       "当日已存在两个场地订单，请自行查看场地信息",
                       config.receiver[0])
    else:
        # 检查订单状态
        while True:
            try:
                book_invite.check_order(venuebooking)
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                time.sleep(random.random() * 0.66)
                continue
        if config.mail:
            weekday = datetime.strptime(config.target_date, "%Y-%m-%d").weekday()
            wday = config.weekd[weekday]
            send_email("自动订场成功",
                       f"{wday}\n{venuebooking[0]['VenueName']}\n{venuebooking[0]['TimeSlots']}",
                       config.receiver[0])
        scheduler.shutdown()




# 定义任务监听器
def job_listener(event):
    # 检查是否是任务错过事件
    if event.code == EVENT_JOB_MISSED:
        print(f"任务 {event.job_id} 错过了执行，正在重新调度...")
        # 重新调度错过的任务
        scheduler.reschedule_job(event.job_id, trigger='date', run_date=datetime.now(), misfire_grace_time=600)


scheduler = BlockingScheduler(executors={'default': ThreadPoolExecutor(max_workers=10)})

if config.way == "scheduled":
    start_date = datetime.now().replace(
        hour=21, minute=50 + int(2 * random.random()), second=int(60 * random.random()))
    job = scheduler.add_job(main, 'date', run_date=start_date, misfire_grace_time=600)
elif config.way == "directly":
    run_date = datetime.now() + timedelta(seconds=1)
    job = scheduler.add_job(main, 'date', run_date=run_date, misfire_grace_time=600)

# 添加任务监听器，监听任务错过和执行完成事件
scheduler.add_listener(job_listener, EVENT_JOB_MISSED | EVENT_JOB_EXECUTED)

# 启动调度器
scheduler.start()





