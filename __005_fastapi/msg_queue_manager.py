import asyncio
import json


class MsgQueueManager:
    def __init__(self):
        self.msg_queue_dict = {}
        self._loop: asyncio.AbstractEventLoop = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def get_msg_queue(self, user_id: str) -> asyncio.Queue:
        if user_id not in self.msg_queue_dict:
            self.msg_queue_dict[user_id] = asyncio.Queue()
        return self.msg_queue_dict[user_id]

    def del_msg_queue(self, user_id: str):
        if user_id in self.msg_queue_dict:
            del self.msg_queue_dict[user_id]

    def _put_sync(self, user_id: str, item: dict):
        """从同步线程安全地向 asyncio.Queue 投递消息"""
        if self._loop is None:
            return  # 未在流式模式下调用（如单节点测试），静默忽略
        queue = self.get_msg_queue(user_id)
        self._loop.call_soon_threadsafe(queue.put_nowait, item)

    # 节点推送进度文本（type=msg）
    def put_msg_content(self, user_id: str, content: str):
        self._put_sync(user_id, {"type": "msg", "msg": content})

    # 终止节点推送最终回答（type=reply）
    def put_reply_content(self, user_id: str, content: str):
        self._put_sync(user_id, {"type": "reply", "msg": content})

    # 流结束信号（type=done）
    def put_done_content(self, user_id: str):
        self._put_sync(user_id, {"type": "done", "msg": ""})

    # 错误信号（type=error）
    def put_error_content(self, user_id: str, content: str):
        self._put_sync(user_id, {"type": "error", "msg": content})


msg_queue_manager = MsgQueueManager()
