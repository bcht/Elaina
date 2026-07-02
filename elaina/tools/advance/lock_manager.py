import weakref
import asyncio

class Lock_Manager:
    def __init__(self):
        self._user_weak_dict = weakref.WeakValueDictionary()#弱引用字典，妈妈再也不用担心我的内存泄露了
        self._lock_dict = asyncio.Lock()#用于字典
    async def get_lock(self,uid:int) -> asyncio.Lock:
        """获取用户专属的异步锁"""
        async with self._lock_dict:
            if self._user_weak_dict.get(uid) is None:
                temp_lock = asyncio.Lock()
                self._user_weak_dict[uid] = temp_lock
            return self._user_weak_dict[uid]
