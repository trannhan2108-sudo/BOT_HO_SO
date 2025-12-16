"""Bot logic that interacts with users and pushes notifications."""

from __future__ import annotations

import logging

from telethon import TelegramClient, events
from telethon.errors import RPCError

from .config import BotSettings
from .sniper import CodeSniper
from .storage import CodeHit, Storage

logger = logging.getLogger(__name__)


class NotificationBot:
    """Telegram bot built with Telethon to deliver code alerts."""

    def __init__(
        self,
        settings: BotSettings,
        storage: Storage,
    ) -> None:
        self.settings = settings
        self.storage = storage
        self.client = TelegramClient("bot", settings.api_id, settings.api_hash)
        self.sniper: CodeSniper | None = None

    async def start(self) -> None:
        await self.client.start(bot_token=self.settings.bot_token)
        self._register_handlers()

    async def run(self) -> None:
        await self.client.run_until_disconnected()

    async def stop(self) -> None:
        await self.client.disconnect()

    def attach_sniper(self, sniper: CodeSniper) -> None:
        self.sniper = sniper

    # region Helpers ----------------------------------------------------------
    async def _broadcast(self, message: str) -> None:
        if not self.storage.has_subscribers():
            return
        for chat_id in self.storage.iter_subscribers():
            try:
                await self.client.send_message(chat_id, message)
            except RPCError as exc:
                logger.warning("Không gửi được tin tới %s: %s", chat_id, exc)

    async def notify_hit(self, hit: CodeHit) -> None:
        parts = [
            "🆕 Mã nạp mới phát hiện!",
            f"• Kênh: {hit.channel}",
            f"• Mã: `{hit.code}`",
            f"• Thời gian: {hit.detected_at}",
        ]
        if hit.link:
            parts.append(f"• Link: {hit.link}")
        parts.append("")
        parts.append(hit.message)
        message = "\n".join(parts)
        await self._broadcast(message)

    def _register_handlers(self) -> None:
        @self.client.on(events.NewMessage(pattern=r"/start"))
        async def _start(event: events.NewMessage.Event) -> None:
            added = self.storage.add_subscriber(event.chat_id)
            if added:
                await event.respond(
                    "Chào bạn! Bot sẽ gửi thông báo khi phát hiện mã mới. "
                    "Dùng /stop để hủy nhận tin."
                )
            else:
                await event.respond("Bạn đã đăng ký nhận thông báo rồi.")

        @self.client.on(events.NewMessage(pattern=r"/stop"))
        async def _stop(event: events.NewMessage.Event) -> None:
            removed = self.storage.remove_subscriber(event.chat_id)
            if removed:
                await event.respond("Đã hủy đăng ký nhận thông báo.")
            else:
                await event.respond("Bạn chưa đăng ký hoặc đã hủy trước đó.")

        @self.client.on(events.NewMessage(pattern=r"/status"))
        async def _status(event: events.NewMessage.Event) -> None:
            subscribers = self.storage.list_subscribers()
            channels = self.settings.watch_channels or ["(Chưa cấu hình)"]
            lines = ["📊 Trạng thái bot:"]
            lines.append(f"• Người nhận thông báo: {len(subscribers)}")
            lines.append("• Theo dõi kênh:")
            lines.extend([f"  - {name}" for name in channels])
            if self.sniper:
                rules = self.sniper.describe_rules()
            else:
                rules = ["(Chưa khởi động sniper)"]
            lines.append("• Bộ lọc mã:")
            lines.extend([f"  - {rule}" for rule in rules])
            await event.respond("\n".join(lines))

        @self.client.on(events.NewMessage(pattern=r"/history"))
        async def _history(event: events.NewMessage.Event) -> None:
            hits = self.storage.get_history(limit=10)
            if not hits:
                await event.respond("Chưa có dữ liệu lịch sử.")
                return
            parts = ["📝 10 mã gần nhất:"]
            for idx, hit in enumerate(hits, start=1):
                line = f"{idx}. `{hit.code}` ({hit.channel})"
                if hit.link:
                    line += f" — {hit.link}"
                parts.append(line)
            await event.respond("\n".join(parts))

        @self.client.on(events.NewMessage(pattern=r"/help"))
        async def _help(event: events.NewMessage.Event) -> None:
            commands = [
                "/start - Đăng ký nhận thông báo",
                "/stop - Hủy nhận thông báo",
                "/status - Xem trạng thái và bộ lọc",
                "/history - Xem 10 mã gần nhất",
                "/help - Danh sách lệnh",
            ]
            await event.respond("Các lệnh hỗ trợ:\n" + "\n".join(commands))

        # fallback: forward non-command help
        @self.client.on(events.NewMessage(pattern=r"/.*"))
        async def _unknown(event: events.NewMessage.Event) -> None:
            if event.text and event.text.startswith("/"):
                await event.respond("Lệnh không hỗ trợ. Gõ /help để xem danh sách.")

