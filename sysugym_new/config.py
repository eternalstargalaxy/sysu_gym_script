from datetime import datetime, timedelta

# 预定日期、时间
# target_date = '2025-02-18'

target_date = (datetime.now().date()+timedelta(days=3)).strftime("%Y-%m-%d")
target_starttime = ["20:00", "21:00"]  #"19:00"

# 预定价格
charge = 30

netiedid = 'xxx'
password = 'xxx'


# 订场方式   直接订场 or 定时抢场
# way = "directly"
way = "scheduled"

if way == "scheduled":
    target_date = (datetime.now().date()+timedelta(days=3)).strftime("%Y-%m-%d")


# 场地优先级
fields_order = ["场地13", "场地12", "场地14", "场地8", "场地9"]


# 接收通知的邮箱
receiver = ['xxxxx@mail2.sysu.edu.cn']

sender = 'xxx@qq.com'         # 消息发送的邮箱
username = 'xxx@qq.com'       # 消息发送的邮箱用户名，直接copy sender
smtpserver = 'smtp.qq.com'           # 消息发送邮箱的服务器（需要与所用的邮箱后缀匹配）
password_email = 'xxxxx'  # 消息发送邮箱的密码/授权码

# 是否发送邮件
mail = False

# 场地名称
Description = "南校园新体育馆羽毛球场（学生）"

# 场地ID 羽毛球
VenueTypeId = "c4f06a7d-bb6b-4a2f-9626-7bebfc4f09ae"

# 日期编号
weekd = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"}




