import sys
import os
import logging
logging.getLogger(__name__)#同步主文件的日志格式

#工具函数    仅允许plugin和main.py使用
from elaina.tools.advance.send_msg import send_msg as _send_message
from elaina.tools.user_json import User as _Users
from elaina.tools.base.time_get import get_formatted_time as _get_time # 这是例外，理论上来说base不允许直接调用，必须走旁路
from elaina.tools.auto_load_json import json_analyze as _json_analyze

#对外提供接口
async def send_msg(msg:str,uid:int,gid:int,mid=None):
    """发送信息  
    没啥需要特别注意的,照着填就行  
    data中均已含有,无需更改类型
    传入:  
    msg -> 需发送的信息  
    uid -> 用户id  
    gid -> 群id  
    mid -> 引用信息id  
    返回:  
    None
    """
    return await _send_message(msg,uid,gid,mid)

def User(uid) -> _Users:
    """
    创建用户对象  
    传入:  
    uid -> 用户id  
    返回:  
    User -> 用户对象
    """
    return _Users(uid)

def get_formatted_time() -> str:
    """
    返回当前时间，格式为 '年份-月份-日期-小时:分钟:秒'  
    传入:  
    None  
    返回:  
    str -> 当前时间
    """
    return _get_time()

async def json_analyze(text:str,uid:int|str,gid:int|str,log_text:str=None) -> dict:
    """
    解析json文本,包含自动强制解析,自动记录日志  
    传入:  
    text -> 需解析的json文本  
    uid -> 用户id  (用于输出日志)  
    gid -> 群id  (用于输出日志)  
    log_text -> 调用模块信息(用于输出日志)(非必要)  
    返回:  
    dict -> 解析后的json文本
    """
    return await _json_analyze(text,uid,gid,log_text)
