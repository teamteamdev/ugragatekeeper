import logging
from typing import Any

import aiogram
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.executor import start_webhook

from ugragatekeeper import utils
from ugragatekeeper.filters import ChannelMessageFilter
from ugragatekeeper.handler import Handler

logger = logging.getLogger(__name__)


def run(domain: str, config: Any, network_options: dict) -> None:
    token = config["bot"]["token"]
    path = utils.get_webhook_path(token)

    async def on_startup(dispatcher: aiogram.Dispatcher) -> None:
        await dispatcher.bot.set_webhook(f"{domain}{path}")
    
    async def on_shutdown(dispatcher: aiogram.Dispatcher) -> None:
        logger.warning("Shutting down")
        await bot.delete_webhook()

    bot = aiogram.Bot(token=token)
    dispatcher = aiogram.Dispatcher(bot)
    dispatcher.middleware.setup(LoggingMiddleware())
    dispatcher.filters_factory.bind(ChannelMessageFilter, event_handlers=[dispatcher.message_handlers])

    handler = Handler(dispatcher, config)
    handler.setup()

    start_webhook(
        dispatcher=dispatcher,
        webhook_path=path,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        **network_options
    )


__all__ = ["run"]
