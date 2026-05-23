from datetime import datetime
def get_formatted_time():
    """返回当前时间，格式为 '年份-月份-日期-小时:分钟:秒'"""
    return datetime.now().strftime("%Y-%m-%d-%H:%M:%S")