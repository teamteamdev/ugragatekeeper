import logging
import sys
import traceback
from typing import Any, Optional

import aiogram
from aiogram import types
from aiogram.dispatcher.webhook import BaseResponse, DeleteMessage, SendMessage

from ugragatekeeper import utils

logger = logging.getLogger(__name__)


class Handler:
    def __init__(self, dispatcher: aiogram.Dispatcher, config: Any):
        self.dispatcher = dispatcher
        self.config = config

    async def log(self, event: str) -> None:
        if "logging" in self.config["modules"]:
            await self.dispatcher.bot.send_message(
                chat_id=self.config["modules"]["logging"]["chat_id"],
                text=event,
                disable_web_page_preview=True,
                disable_notification=True,
                parse_mode="HTML"
            )
        else:
            logger.info("%s", event)

    async def remove(self, message: types.Message, reason: str) -> BaseResponse:
        await self.log(utils.format_message(message, reason))
        return DeleteMessage(message.chat.id, message.message_id)

    async def remove_join(self, message: types.Message) -> BaseResponse:
        return await self.remove(message, "join")

    async def remove_leave(self, message: types.Message) -> BaseResponse:
        return await self.remove(message, "leave")

    async def remove_channel(self, message: types.Message) -> Optional[BaseResponse]:
        self_chat = await self.dispatcher.bot.get_chat(message.chat.id)
        if self_chat.linked_chat_id == message.sender_chat.id:
            return
        return await self.remove(message, "channel")

    async def check_answer(self, message: types.Message) -> Optional[BaseResponse]:
        if self.config["modules"]["process_join_requests"]["answer"] in message.text.lower():
            try:
                await self.dispatcher.bot.approve_chat_join_request(chat_id=self.config["bot"]["chat_id"], user_id=message.chat.id)
                return SendMessage(chat_id=message.chat.id, text=self.config["modules"]["process_join_requests"]["correct_feedback"])
            except aiogram.utils.exceptions.BadRequest as exc:
                if exc.check("user_already_participant"):
                    return SendMessage(chat_id=message.chat.id, text=self.config["modules"]["process_join_requests"]["approve_fail_feedback"])
                
                logging.exception("Can not approve request")
                await self.log(f"Could not approve request from {message.chat.id}")
                return 
        else:
            return SendMessage(chat_id=message.chat.id, text=self.config["modules"]["process_join_requests"]["incorrect_feedback"])

    async def join_request(self, request: types.ChatJoinRequest) -> None:
        await self.log(utils.format_join_request(request))
        await self.dispatcher.bot.send_message(
            chat_id=request.from_user.id,
            text=self.config["modules"]["process_join_requests"]["question"]
        )

    def error(self, update: types.Update, exc: Exception) -> bool:
        logging.error("Error while processing update", exc_info=exc)
        return True


    def setup(self):
        if "remove_joins" in self.config["modules"]:
            self.dispatcher.register_message_handler(
                self.remove_join,
                content_types=types.ContentTypes.NEW_CHAT_MEMBERS,
                chat_id=self.config["bot"]["chat_id"]
            )

        if "remove_leaves" in self.config["modules"]:
            self.dispatcher.register_message_handler(
                self.remove_leave,
                content_types=types.ContentTypes.LEFT_CHAT_MEMBER,
                chat_id=self.config["bot"]["chat_id"]
            )

        if "remove_channel_messages" in self.config["modules"]:
            self.dispatcher.register_message_handler(
                self.remove_channel,
                by_channel_except=self.config["modules"]["remove_channel_messages"].get("exceptions", []),
                chat_id=self.config["bot"]["chat_id"]
            )

        if "process_join_requests" in self.config["modules"]:
            self.dispatcher.register_chat_join_request_handler(
                self.join_request,
                request_chat_id=self.config["bot"]["chat_id"]
            )
            self.dispatcher.register_message_handler(
                self.check_answer,
                chat_type=types.ChatType.PRIVATE
            )

        self.dispatcher.register_errors_handler(self.error)
