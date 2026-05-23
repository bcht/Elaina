import sys
import os
import logging
logging.getLogger(__name__)#同步主文件的日志格式
sys.path.append(os.path.dirname(os.path.dirname(__file__))) #统一导入上级目录

#工具函数    仅允许plugin和main.py使用
from tools.send_msg import send_msg as send_message
from tools.user_json import User as Users
from tools.time_get import get_formatted_time as get_time

#对外提供接口
async def send_msg(msg,uid : int,gid : int,mid = None):
    """发送信息  
    没啥需要特别注意的,照着填就行
    """
    return await send_message(msg,uid,gid,mid)

def User(uid,path):
    """创建用户对象"""
    return Users(uid,path)

def get_formatted_time():
    """返回当前时间，格式为 '年份-月份-日期-小时:分钟:秒'"""
    return get_time()
