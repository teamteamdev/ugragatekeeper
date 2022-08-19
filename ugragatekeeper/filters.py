import logging
from typing import Optional

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

logger = logging.getLogger()


class ChannelMessageFilter(BoundFilter):
    key = "by_channel_except"

    def __init__(self, by_channel_except: list[int] = []):
        self.allowed_channels = by_channel_except

    async def check(self, obj: types.Message) -> bool:
        return (obj.sender_chat is not None
                and obj.sender_chat.id != obj.chat.id
                and obj.sender_chat.id not in self.allowed_channels)


class RequestChatIDFilter(BoundFilter):
    key = "request_chat_id"

    def __init__(self, request_chat_id: Optional[int] = None):
        self.chat_id: Optional[int] = request_chat_id

    async def check(self, obj: types.ChatJoinRequest):
        return self.chat_id == obj.chat.id
