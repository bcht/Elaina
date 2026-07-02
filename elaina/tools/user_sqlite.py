import json
import asyncio
import logging
import aiosqlite
import copy

from elaina.tools.advance.check_user_template import user_template,is_user_template_complete
import elaina.common.setting as setting


logger = logging.getLogger(__name__)#同步主文件的日志格式

class User:
    def __init__(self,uid):
        self.uid = uid
        logger.debug(f'setting.db的值为:{setting.db}')
        logger.debug(f'setting库内存地址:{id(setting)}')
    
    async def load(self) -> dict:
        """若存在用户文件，则返回用户的信息  
        若不存在，则返回初始模版并创建  
        输入:  
        None  
        输出:  
        dict -> 用户信息  
        模版:  
        "message":[],#消息，包括用户和机器人的  
        "favor":0,#好感度  
        "time":[]"""
        user = copy.deepcopy(user_template)#防串……
        async with setting.db.execute('SELECT favor FROM users WHERE uid = ?',(self.uid,)) as cursor:# 读用户好感度
            row = await cursor.fetchone()#只导出一个元组
            if  row is None:#如果不存在该用户
                await setting.db.execute('INSERT INTO users (uid, favor) VALUES (?, ?)',(self.uid,user_template["favor"],))#依照模版创建
                await setting.db.commit()
                return user#直接返回模版
            else:
                user['favor'] = row[0]
        async with setting.db.execute('SELECT role, content, time FROM messages WHERE uid = ? ORDER BY id',(self.uid,)) as cursor:# 读用户聊天记录
            rows = await cursor.fetchall()#全部转为列表
            if rows:#若存在记录
                logger.debug(f'sqlite_load_row为{len(rows)}条')
                time_i = 0
                for i in rows:#循环解压
                    user['message'].append({'role':i[0],'content':i[1]})
                    if time_i % 2 == 0:
                        user['time'].append(i[2])
                    time_i += 1
        logger.debug(f'将要传输的user字典内容：{user}')
        return user
    
    async def delete(self) -> None:
        """重置用户文件，什么都不返回  
        输入:  
        None  
        输出:  
        None"""
        try:
            await setting.db.execute("BEGIN")
            await setting.db.execute('UPDATE users SET favor = ? WHERE uid = ?',(user_template["favor"],self.uid,))
            cursor = await setting.db.execute('DELETE FROM messages WHERE uid = ?',(self.uid,))
            logger.debug(f'删除了{cursor.rowcount}条记录')
            await setting.db.commit()
        except Exception:
            await setting.db.rollback()
            logger.exception('delete_数据库操作失败')
    
    async def write(self,data) -> None:
        """将用户信息写入文件  
        传入:
        data -> dict
        输出:  
        None  
        注意，别传入一个不是字典的玩意  
        不要让我在修bug的时候看到这玩意报错!!!"""
        if not is_user_template_complete(data):#我不管，就算我提醒了我也要做个防备措施
            logger.error(f'{self.uid}模版不匹配！')
            raise ValueError('模版不匹配！李在干什麽？')
        logger.debug(f'data内容：{data}')
        try:
            await setting.db.execute("BEGIN")
            cursor = await setting.db.execute('UPDATE users SET favor = ? WHERE uid = ?',(data["favor"],self.uid,))
            if cursor.rowcount == 0:#用户不存在，创建新用户
                await setting.db.execute("INSERT INTO users (uid, favor) VALUES (?, ?)", (self.uid, data["favor"]))#万一呢？

            cursor = await setting.db.execute('DELETE FROM messages WHERE uid = ?',(self.uid,))
            logger.debug(f'删除了{cursor.rowcount}条记录')
            messages_data = []
            for i in range(len(data["message"])):#对齐
                messages_data.append((
                    self.uid,
                    data["message"][i]["role"],
                    data["message"][i]["content"],
                    data["time"][int(i/2)],
                ))
            await setting.db.executemany('INSERT INTO messages (uid, role, content, time) VALUES (?, ?, ?, ?)',messages_data)#多条插入
            await setting.db.commit()
        except Exception as e:
            await setting.db.rollback()
            raise e
