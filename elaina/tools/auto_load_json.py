import json
import logging
import ast
import re

from elaina.common.setting import FORCE_JSON
from elaina.tools.advance.send_msg import send_msg # 允许高级模块调用下层模块

logger = logging.getLogger(__name__)#同步主文件的日志格式

async def _try_to_send_msg(msg:str,uid:int,gid:int,mid=None):
    """
    用于自动处理uid和gid为None的情况
    仅可用于json_analyze()内部使用
    """
    if uid == None and gid == None:
        logger.warning('uid和gid同时为None，不予发送')
        return
    await send_msg(msg,uid,gid,mid)

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
    try:
        return json.loads(text)#正常严格解析
    except json.JSONDecodeError:
        if FORCE_JSON:
            logger.warning(f'尝试强制解析')
            try:
                match = re.search(r'\{.*\}', text, re.DOTALL)#假设一下上层发来了一个奇奇怪怪的字符串
                if not match:
                    logger.warning('强制解析失败，未找到json结构')
                    return {}
                return ast.literal_eval(match.group(0))#尝试非严格安全解析
            except Exception:
                await _try_to_send_msg(f'强制解析出现错误，请联系管理员,调用模块:{log_text}',uid,gid)
                logger.exception(f'强制解析错误,调用模块:{log_text}')
                return {}
        else:
            await _try_to_send_msg(f'解析出现错误，请联系管理员,调用模块:{log_text}',uid,gid)
            logger.exception(f'解析出现错误，真发生了?调用模块:{log_text}')
            return {}
    except Exception:
        await _try_to_send_msg(f'解析出现错误，请联系管理员,调用模块:{log_text}',uid,gid)
        #这种情况很少发生，不过为了输出的美观，还是不要在没结构化的情况下输出吧
        #不过懂点的朋友可以自行修改，毕竟这是我个人的喜好
        logger.exception(f'解析出现错误，真发生了?调用模块:{log_text}')
        return {}
