"""Entry point to run the Telegram code hunting bot."""

from __future__ import annotations

import asyncio
import logging

from .bot_service import NotificationBot
from .config import BotSettings
from .sniper import CodeSniper
from .storage import Storage

logger = logging.getLogger(__name__)


async def _main_async(settings: BotSettings | None = None) -> None:
    if settings is None:
        settings = BotSettings()  # type: ignore[call-arg]
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    storage = Storage(settings.data_dir, history_size=settings.history_size)
    bot = NotificationBot(settings, storage)
    sniper = CodeSniper(settings, storage)
    bot.attach_sniper(sniper)
    sniper.register_callback(bot.notify_hit)

    await sniper.start()
    await bot.start()

    logger.info("Bot và sniper đã khởi động. Sẵn sàng săn mã!")

    await asyncio.gather(sniper.run(), bot.run())


def run(settings: BotSettings | None = None) -> None:
    """Run the Telegram bot (blocking call)."""

    try:
        asyncio.run(_main_async(settings))
    except KeyboardInterrupt:
        logger.info("Đã nhận tín hiệu dừng. Đóng bot...")


if __name__ == "__main__":
    run()
