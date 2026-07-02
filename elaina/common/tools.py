import sys
import os
import logging

#工具函数    仅允许plugin和main.py使用
from elaina.tools.advance.send_msg import send_msg as _send_message
from elaina.tools.user_json import User as _Json_User
from elaina.tools.base.time_get import get_formatted_time as _get_time # 这是例外，理论上来说base不允许直接调用，必须走旁路
from elaina.tools.auto_load_json import json_analyze as _json_analyze
from elaina.tools.advance.check_user_template import is_user_template_complete as _is_user_template_complete,user_template as _user_template
from elaina.tools.user_sqlite import User as _SQLite_User
from elaina.common.setting import DATABASE_TYPE as _db_type
from elaina.tools.advance.lock_manager import Lock_Manager as _Lock_Manager

user_template = _user_template# 定义用户模版
_db_type = _db_type.lower()

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

def User(uid) -> object:
    """
    创建用户对象  
    传入:  
    uid -> 用户id  
    返回:  
    User -> 用户对象
    """
    if _db_type == "sqlite":#要的就是上层无感！
        return _SQLite_User(uid)
    elif _db_type == "json":
        return _Json_User(uid)

def get_formatted_time() -> str:
    """
    返回当前时间，格式为 '年份-月份-日期-小时:分钟:秒'  
    传入:  
    None  
    返回:  
    str -> 当前时间  
    **注意该函数为同步函数**  
    """
    return _get_time()

async def json_analyze(text:str,uid:int|str=None,gid:int|str=None,log_text:str=None) -> dict:
    """
    解析json文本,包含自动强制解析,自动记录日志  
    传入:  
    text -> 需解析的json文本  
    uid -> 用户id  (用于输出日志)(非必要)  
    gid -> 群id  (用于输出日志)(非必要)  
    log_text -> 调用模块信息(用于输出日志)(非必要)  
    返回:  
    dict -> 解析后的json文本  
    若失败: 返回{}  
    """
    return await _json_analyze(text,uid,gid,log_text)

def is_user_template_complete(data : dict ) -> bool:
    """
    输入  
    data->dict  
    输出  
    bool  
    用于检查用户信息是否符合模版，返回True表示符合模版，返回False表示不符合模版  
    防呆不防傻，只要我不傻，并且用这个，估计就没毛病  
    **注意该函数为同步函数**  
    """
    return _is_user_template_complete(data)

def Lock_Manager() -> object:
    """返回锁管理器"""
    return _Lock_Manager()
