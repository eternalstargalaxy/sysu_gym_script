import datetime

# netidid,password
best_netiedid = ""
best_password = ""

# 场地、时间(可以只选一个也可以多选,太少有可能失败)
best_fields = ["场地13", "场地12", "场地14", "场地8", "场地9"]
best_playtimes = ['20:01-21:00', '19:01-20:00', '21:01-22:00']


#接收通知的邮箱
receiver = ['xxx@mail2.sysu.edu.cn']

sender = 'xxx@qq.com'         # 消息发送的邮箱

smtpserver = 'smtp.qq.com'           # 消息发送邮箱的服务器（需要与所用的邮箱后缀匹配）
password_email = 'xxx'              # 消息发送邮箱的密码/授权码


username = sender
# 选择日期(days=1表示第二天)
now = datetime.datetime.now()
if now.hour >= 22:
    bookdate = ((now + datetime.timedelta(days=2)).strftime("%Y-%m-%d"))
    monidate = ((now + datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
else:
    bookdate = ((now + datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
    monidate = (now.strftime("%Y-%m-%d"))

weekday = datetime.datetime.strptime(bookdate, "%Y-%m-%d").weekday()


#不用改
weekd = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"}
orderid = ""
s = "522"   # 场地网页信息 522





