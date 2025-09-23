"""Configuration helpers for the Telegram top-up code sniper."""

from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import BaseModel, BaseSettings, Field, validator


DEFAULT_PATTERNS = [
    r"\b\d{12,16}\b",  # chuỗi chỉ gồm số dài 12-16 ký tự
    r"\b[A-Z0-9]{10,16}\b",  # mã hỗn hợp in hoa & số
]


def _split_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


class WatchRule(BaseModel):
    pattern: str = Field(..., description="Biểu thức regex để tìm mã")
    description: str | None = Field(
        default=None, description="Ghi chú hiển thị trong phần /patterns"
    )


class BotSettings(BaseSettings):
    """Thiết lập chính cho bot săn mã thẻ."""

    api_id: int = Field(..., alias="TELEGRAM_API_ID", description="Telegram api_id")
    api_hash: str = Field(
        ..., alias="TELEGRAM_API_HASH", description="Telegram api_hash"
    )
    bot_token: str = Field(
        ..., alias="TELEGRAM_BOT_TOKEN", description="Bot token do BotFather cấp"
    )
    user_session: str = Field(
        default="sniper_session",
        alias="TELETHON_SESSION",
        description="Tên file session dùng cho tài khoản người dùng",
    )
    watch_channels: List[str] = Field(
        default_factory=list,
        alias="TELEGRAM_WATCH_CHANNELS",
        description="Danh sách channel/group cần theo dõi (username, link hoặc ID)",
    )
    rules: List[WatchRule] = Field(
        default_factory=lambda: [
            WatchRule(pattern=DEFAULT_PATTERNS[0], description="Chuỗi số 12-16 ký tự"),
            WatchRule(
                pattern=DEFAULT_PATTERNS[1],
                description="Chuỗi in hoa + số 10-16 ký tự",
            ),
        ],
        alias="SNIPER_RULES",
        description="Danh sách pattern dùng để bắt mã",
    )
    history_size: int = Field(
        default=50, alias="SNIPER_HISTORY_SIZE", ge=1, le=500, description="Số bản ghi lịch sử lưu"
    )
    data_dir: Path = Field(
        default=Path("runtime"),
        alias="SNIPER_DATA_DIR",
        description="Thư mục lưu session/history/subscribers",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = ""

    @validator("watch_channels", pre=True)
    def _parse_watch_channels(cls, value):  # type: ignore[override]
        if isinstance(value, str):
            return _split_list(value)
        return value

    @validator("rules", pre=True)
    def _parse_rules(cls, value):  # type: ignore[override]
        if isinstance(value, str):
            entries = _split_list(value)
            return [WatchRule(pattern=pattern) for pattern in entries]
        if value is None:
            return []
        return value

    @validator("data_dir", pre=True)
    def _ensure_path(cls, value):  # type: ignore[override]
        if isinstance(value, str):
            return Path(value)
        return value
