"""Local persistent storage for subscribers and history."""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Deque, Iterable, List, Set


@dataclass
class CodeHit:
    code: str
    channel: str
    message: str
    link: str | None
    detected_at: str

    @classmethod
    def create(
        cls, *, code: str, channel: str, message: str, link: str | None
    ) -> "CodeHit":
        timestamp = datetime.now(tz=timezone.utc).isoformat()
        short_msg = message.strip()
        if len(short_msg) > 300:
            short_msg = short_msg[:297] + "..."
        return cls(code=code, channel=channel, message=short_msg, link=link, detected_at=timestamp)


class Storage:
    """Persist subscribers & history into JSON files."""

    def __init__(self, base_dir: Path, history_size: int = 50) -> None:
        self.base_dir = base_dir
        self.history_size = history_size
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.subscribers_path = self.base_dir / "subscribers.json"
        self.history_path = self.base_dir / "history.json"
        self._subscribers: Set[int] = set()
        self._history: Deque[CodeHit] = deque(maxlen=history_size)
        self._load()

    # region Loading & saving -------------------------------------------------
    def _load(self) -> None:
        if self.subscribers_path.exists():
            try:
                data = json.loads(self.subscribers_path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self._subscribers = {int(item) for item in data}
            except Exception:
                self._subscribers = set()
        if self.history_path.exists():
            try:
                raw_history = json.loads(self.history_path.read_text(encoding="utf-8"))
                if isinstance(raw_history, list):
                    for entry in raw_history[-self.history_size :]:
                        if not isinstance(entry, dict):
                            continue
                        hit = CodeHit(
                            code=str(entry.get("code", "")),
                            channel=str(entry.get("channel", "")),
                            message=str(entry.get("message", "")),
                            link=entry.get("link"),
                            detected_at=str(entry.get("detected_at", "")),
                        )
                        self._history.append(hit)
            except Exception:
                self._history.clear()

    def _flush_subscribers(self) -> None:
        payload = sorted(self._subscribers)
        self.subscribers_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _flush_history(self) -> None:
        payload = [asdict(item) for item in list(self._history)]
        self.history_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # endregion ---------------------------------------------------------------

    # region Subscribers ------------------------------------------------------
    def add_subscriber(self, chat_id: int) -> bool:
        if chat_id in self._subscribers:
            return False
        self._subscribers.add(chat_id)
        self._flush_subscribers()
        return True

    def remove_subscriber(self, chat_id: int) -> bool:
        if chat_id not in self._subscribers:
            return False
        self._subscribers.remove(chat_id)
        self._flush_subscribers()
        return True

    def list_subscribers(self) -> List[int]:
        return sorted(self._subscribers)

    # endregion ---------------------------------------------------------------

    # region History ----------------------------------------------------------
    def push_history(self, item: CodeHit) -> None:
        self._history.append(item)
        self._flush_history()

    def get_history(self, limit: int = 10) -> List[CodeHit]:
        limit = max(1, min(limit, self.history_size))
        return list(list(self._history)[-limit:])

    # endregion ---------------------------------------------------------------

    def has_subscribers(self) -> bool:
        return bool(self._subscribers)

    def iter_subscribers(self) -> Iterable[int]:
        return iter(self._subscribers)
