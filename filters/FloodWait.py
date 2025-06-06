from aiogram.filters import BaseFilter
from aiogram.types import Message
import time


class RateLimitFilter(BaseFilter):
    def __init__(self, limit: float, expiration_time: float = 3600):
        self.limit = limit
        self.expiration_time = expiration_time
        self.last_request_time = {}

    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        current_time = time.time()

        self._cleanup_expired(current_time)

        if user_id in self.last_request_time:
            last_time = self.last_request_time[user_id]
            if (current_time - last_time) < self.limit:
                return False

        self.last_request_time[user_id] = current_time
        return True

    def _cleanup_expired(self, current_time: float):
        expired_keys = [
            user_id
            for user_id, last_time in self.last_request_time.items()
            if (current_time - last_time) > self.expiration_time
        ]
        for user_id in expired_keys:
            del self.last_request_time[user_id]
