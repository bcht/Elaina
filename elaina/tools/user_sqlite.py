import json
import asyncio
import logging
import aiosqlite

from elaina.tools.advance.check_user_template import user_template,is_user_template_complete
from elaina.common.setting import db

logger = logging.getLogger(__name__)#同步主文件的日志格式

class User:
    def __init__(self,uid):
        self.uid = uid
    
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
        user = user_template
        async with db.execute('SELECT favor FROM users WHERE uid = ?',(self.uid,)) as cursor:# 读用户好感度
            row = await cursor.fetchone()#只导出一个元组
            if  row is None:#如果不存在该用户
                await db.execute('INSERT INTO users (uid, favor) VALUES (?, ?)',(self.uid,user_template["favor"],))#依照模版创建
                await db.commit()
                return user#直接返回模版
            else:
                user['favor'] = row[0]
        async with db.execute('SELECT role, content, time FROM messages WHERE uid = ? ORDER BY id',(self.uid,)) as cursor:# 读用户聊天记录
            rows = await cursor.fetchall()#全部转为列表
            if rows:#若存在记录
                for i in rows:#循环解压
                    user['message'].append({'role':i[0],'content':i[1]})
                    user['time'].append(i[2])
        return user
    
    async def delete(self) -> None:
        """重置用户文件，什么都不返回  
        输入:  
        None  
        输出:  
        None"""
        await db.execute('UPDATE users SET favor = ? WHERE uid = ?',(user_template["favor"],self.uid,))
        await db.execute('DELETE FROM messages WHERE uid = ?',(self.uid,))
        await db.commit()
    
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
        cursor = await db.execute('UPDATE users SET favor = ? WHERE uid = ?',(data["favor"],self.uid,))
        if cursor.rowcount == 0:#用户不存在，创建新用户
            await db.execute("INSERT INTO users (uid, favor) VALUES (?, ?)", (self.uid, data["favor"]))#万一呢？
        
        await db.execute('DELETE FROM messages WHERE uid = ?',(self.uid,))
        messages_data = []
        for i in range(len(data["message"])):#对齐
            messages_data.append((
                self.uid,
                data["message"][i]["role"],
                data["message"][i]["content"],
                data["time"][i]
            ))
        await db.executemany('INSERT INTO messages (uid, role, content, time) VALUES (?, ?, ?, ?)',messages_data)#多条插入
        await db.commit()
