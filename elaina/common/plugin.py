import sys
import os
import logging
import asyncio
logging.getLogger(__name__)#同步主文件的日志格式
sys.path.append(os.path.dirname(os.path.dirname(__file__))) #统一导入上级目录

#仅允许main.py调用
from plugin.user_ai_msgreply import auto_reply_message as user_ai

async def ai_auto_reply_message(data:dict):
    return await user_ai(data)
