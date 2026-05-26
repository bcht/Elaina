import json
import logging
import ast

from elaina.common.setting import FORCE_JSON
from elaina.tools.advance.send_msg import send_msg # 允许高级模块调用下层模块

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
    若失败: 返回{}
    """
    try:
        return json.loads(text)#正常严格解析
    except json.JSONDecodeError:
        if FORCE_JSON:
            logging.warning(f'尝试强制解析')
            try:
                return ast.literal_eval(text)#尝试非严格安全解析
            except Exception:
                await send_msg(f'强制解析出现错误，请联系管理员,调用模块:{log_text}',uid,gid)
                logging.exception(f'强制解析错误,调用模块:{log_text}')
                return {}
        else:
            await send_msg(f'解析出现错误，请联系管理员,调用模块:{log_text}',uid,gid)
            logging.exception(f'解析出现错误，真发生了?调用模块:{log_text}')
            return {}
    except Exception:
        await send_msg(f'解析出现错误，请联系管理员,调用模块:{log_text}',uid,gid)
        #这种情况很少发生，不过为了输出的美观，还是不要在没结构化的情况下输出吧
        #不过懂点的朋友可以自行修改，毕竟这是我个人的喜好
        logging.exception(f'解析出现错误，真发生了?调用模块:{log_text}')
        return {}
