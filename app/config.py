"""Cấu hình đọc từ biến môi trường (file .env)."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # Claude API: SDK tự đọc ANTHROPIC_API_KEY, không cần truyền vào code.
    claude_model: str = os.getenv("CLAUDE_MODEL", "claude-opus-5-5")
    claude_effort: str = os.getenv("CLAUDE_EFFORT", "medium")

    # Thông tin thương hiệu, đưa vào lời dặn cho AI.
    brand_name: str = os.getenv("BRAND_NAME", "Cửa hàng của anh")
    brand_voice: str = os.getenv(
        "BRAND_VOICE", "thân thiện, gần gũi, chuyên nghiệp, xưng 'mình' và gọi khách là 'bạn'"
    )

    # Telegram: gửi bản nháp để duyệt. Để trống thì bỏ qua bước này.
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    output_dir: Path = field(default_factory=lambda: Path(os.getenv("OUTPUT_DIR", "output")))


settings = Settings()
