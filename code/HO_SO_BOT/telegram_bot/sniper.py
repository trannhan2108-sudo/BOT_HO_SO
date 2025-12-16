"""Telethon client that watches channels for recharge codes."""

from __future__ import annotations

import logging
import re
from typing import Awaitable, Callable, Iterable, List, Sequence

from telethon import TelegramClient, events
from telethon.errors import RPCError

from .config import BotSettings, WatchRule
from .storage import CodeHit, Storage

logger = logging.getLogger(__name__)


class CodeSniper:
    """Listen to Telegram channels and detect top-up codes using regex rules."""

    def __init__(
        self,
        settings: BotSettings,
        storage: Storage,
    ) -> None:
        self.settings = settings
        self.storage = storage
        self.client = TelegramClient(
            str(settings.data_dir / settings.user_session),
            settings.api_id,
            settings.api_hash,
        )
        self.rules: List[WatchRule] = list(settings.rules)
        self._callbacks: List[Callable[[CodeHit], Awaitable[None]]] = []
        self._started = False

    # region Lifecycle --------------------------------------------------------
    async def start(self) -> None:
        if self._started:
            return
        await self.client.start()
        if self.settings.watch_channels:
            logger.info("Loading watch targets: %s", self.settings.watch_channels)
            await self._ensure_targets(self.settings.watch_channels)
        self.client.add_event_handler(
            self._on_new_message,
            events.NewMessage(chats=self._resolve_watch_targets()),
        )
        self._started = True

    async def run(self) -> None:
        if not self._started:
            await self.start()
        await self.client.run_until_disconnected()

    async def stop(self) -> None:
        if self._started:
            await self.client.disconnect()
            self._started = False

    # endregion ---------------------------------------------------------------

    def _resolve_watch_targets(self) -> Sequence[str] | None:
        if not self.settings.watch_channels:
            return None
        return tuple(self.settings.watch_channels)

    async def _ensure_targets(self, targets: Iterable[str]) -> None:
        for target in targets:
            try:
                await self.client.get_entity(target)
            except RPCError as exc:
                logger.warning("Không thể truy cập %s: %s", target, exc)
            except ValueError:
                logger.warning("Không xác định được kênh %s", target)

    def register_callback(self, callback: Callable[[CodeHit], Awaitable[None]]) -> None:
        self._callbacks.append(callback)

    # region Helpers ----------------------------------------------------------
    @property
    def compiled_rules(self) -> List[re.Pattern[str]]:
        return [re.compile(rule.pattern, flags=re.IGNORECASE) for rule in self.rules]

    def _extract_codes(self, text: str) -> List[str]:
        codes: List[str] = []
        for pattern in self.compiled_rules:
            for match in pattern.findall(text):
                normalized = match.strip()
                if normalized and normalized not in codes:
                    codes.append(normalized)
        return codes

    async def _notify(self, hit: CodeHit) -> None:
        for callback in self._callbacks:
            try:
                await callback(hit)
            except Exception:
                logger.exception("Callback %s failed", callback)

    # endregion ---------------------------------------------------------------

    async def _on_new_message(self, event: events.NewMessage.Event) -> None:
        message_text = event.raw_text or ""
        codes = self._extract_codes(message_text)
        if not codes:
            return
        chat = await event.get_chat()
        channel_name = getattr(chat, "title", None) or getattr(chat, "username", "Unknown")
        link = None
        if getattr(event, "is_channel", False):
            username = getattr(chat, "username", None)
            if username:
                link = f"https://t.me/{username}/{event.id}"
        for code in codes:
            hit = CodeHit.create(
                code=code,
                channel=str(channel_name),
                message=message_text,
                link=link,
            )
            self.storage.push_history(hit)
            await self._notify(hit)
            logger.info("Detected code %s from %s", code, channel_name)

    # region Diagnostics ------------------------------------------------------
    def describe_rules(self) -> List[str]:
        items: List[str] = []
        for idx, rule in enumerate(self.rules, start=1):
            if rule.description:
                items.append(f"{idx}. {rule.pattern} — {rule.description}")
            else:
                items.append(f"{idx}. {rule.pattern}")
        return items

    # endregion ---------------------------------------------------------------
