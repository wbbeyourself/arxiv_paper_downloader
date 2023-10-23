import datetime
import pytz

# 获取当前的UTC时间
utc_now = datetime.datetime.utcnow()

# 创建UTC时区对象
utc_tz = pytz.timezone('UTC')

# 创建北京时区对象
beijing_tz = pytz.timezone('Asia/Shanghai')

# 将UTC时间转换为北京时间
beijing_now = utc_now.astimezone(beijing_tz)

# 打印结果
print("UTC时间:", utc_now)
print("北京时间:", beijing_now)
