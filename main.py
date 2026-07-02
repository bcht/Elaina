from config import *
from fastapi import *
from datetime import datetime
from fastapi.responses import *
from contextlib import asynccontextmanager# 用于生命周期函数
#不要管没有调用的库，总有一天会用的，额，不用反正也没啥影响
import os
import json
import requests
import ast
import logging
import importlib
import ota
import uvicorn
import httpx
import asyncio
import aiofiles
import aiosqlite

from elaina.common.plugin import ai_auto_reply_message,send_msg
import elaina.common.setting as setting# 挂数据库对象

#首先，去他丫的LOGO
#我肯定是不会写LOGO，占地

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
    )
#在没有错误日志的情况下诊断任何问题无异于闭眼开车——Apache官方文档
logger = logging.getLogger(__name__)#方便查看是哪个模块

path =  os.path.dirname(__file__) #文件路径
logger.debug(f'路径:{path}')
if not os.path.exists(os.path.join(path,'user_json')):#初始化ing
    logger.warning('用户数据库不存在，创建')
    os.makedirs(os.path.join(path,'user_json'))
if not os.path.exists(os.path.join(path,'group_json')):
    logger.warning('群聊数据库不存在，创建')
    os.makedirs(os.path.join(path,'group_json'))

async def database_init():
    # 初始化数据库
    logger.info('正在初始化数据库')
    db_type = DATABASE_TYPE.lower()# 转小写方便判断
    if db_type == 'sqlite':
        await setting.db.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            uid INTEGER PRIMARY KEY,
            favor INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INTEGER,
            role TEXT,
            content TEXT,
            time TEXT,
            FOREIGN KEY (uid) REFERENCES users(uid)
        );
        """)
        await setting.db.commit()

@asynccontextmanager
async def lifespan(app : FastAPI):
    # 控制FastAPI的生命周期函数,人话就是yield前面的是启动时做的,后面的是停止时做的
    db_type = DATABASE_TYPE.lower()# 转小写方便判断
    logger.debug(f'数据库类型:{db_type}')
    logger.debug(f'setting库内存地址:{id(setting)}')
    db = None
    if db_type == 'sqlite':
        logger.info('确定为sqlite数据库')
        logger.info('正在创建sqlite数据库')
        try:
            db = await aiosqlite.connect('elaina.db')# 连接并创建数据库对象
        except aiosqlite.OperationalError:
            logger.error('无法连接数据库，请检查数据库文件权限')
            raise #抛出错误，强制停止
        setting.db = db
        await database_init()

    yield# 这里指的是正常跑HTTP服务

    if db_type == 'sqlite' and db:
        logger.info('正在关闭sqlite数据库')
        await db.close()# 确保关闭


SERVER = FastAPI(title='Elaina',lifespan=lifespan)
CLIENT_VERSION = 'v2.2.2'# 机器人版本，用于OTA，不要修改
KEEP_FILE = ['config.py','user_json','group_json','elaina.db']

def get_formatted_time():
    """返回当前时间，格式为 '年份-月份-日期-小时:分钟:秒'"""
    return datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

# def hot_reload_config():
#     """用于热重载配置文件"""
#     logger.info('正在热重载配置文件')
#     importlib.reload(config)
#     globals().update({k: v for k, v in vars(config).items() if not k.startswith("_")})
#     """
#     我承认这一大堆我也看不懂
#     反正就是把那一大堆变量读进来,赋值给全局变量
#     并且忽视私有变量(下划线开头)
#     """
"""
因为主要的功能被移到后端了,因此热加载不能用了QAQ
"""

@SERVER.post('/')
async def auto_reply_message(data: dict):
    uid = data.get("user_id")#目标qq
    gid = data.get("group_id")#群聊qq
    mid = data.get("message_id")#消息编号
    msg = data.get("raw_message")#消息

    if msg is not None and (msg[0]=='/' or msg.startswith(f'[CQ:at,qq={BOT_QQ}]')):#若消息不为空，且开头为斜杠或at的情况下受理
        msg = msg.replace("&#91;", "[").replace("&#93;", "]").replace("&amp;", "&").replace("&#44;", ",")#转码
        data['msg'] = msg
        if uid==2854196310:#这里是防Q群管家
            logger.debug('Q群管家at你了')
            return {}
        #运行已在此注册的功能
        await ai_auto_reply_message(data)

        if msg == '/help':#用于获取帮助
            try:
                with open('help.txt','r',encoding='utf-8') as f:#防手欠x2
                    await send_msg(f'{f.read()}',uid,gid)
            except FileNotFoundError:
                await send_msg('未找到帮助文档文件',uid,gid)
                logger.exception('未找到帮助文档文件，请确认help.txt是否存在且未重命名')
                return {}
            return {}
        
    return {}

if __name__ == '__main__':#但愿没人闲的没事把这玩意当模块跑
    logger.info(f'当前版本:{CLIENT_VERSION}')
    if OTA_ALLOW:
        logger.info('正在检查更新...')
        success, msg = ota.ota_update(CLIENT_VERSION, GITHUB_REPO, auto_restart=True)
        logger.info(msg)
        
    uvicorn.run(SERVER,host=CLIENT_ADDRESS,port=CLIENT_PORT)#每日禁用debug(1/1)
