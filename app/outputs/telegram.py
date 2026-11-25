"""Gửi bản nháp qua Telegram để anh duyệt trên điện thoại."""

import logging

import httpx

from app.config import Settings

log = logging.getLogger(__name__)

TELEGRAM_LIMIT = 4000  # Telegram giới hạn 4096 ký tự mỗi tin


def send_for_review(text: str, settings: Settings) -> bool:
    if not (settings.telegram_bot_token and settings.telegram_chat_id):
        log.info("Chưa cấu hình Telegram, bỏ qua bước gửi duyệt")
        return False

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    chunks = [text[i : i + TELEGRAM_LIMIT] for i in range(0, len(text), TELEGRAM_LIMIT)]
    with httpx.Client(timeout=30) as http:
        for chunk in chunks:
            resp = http.post(url, json={"chat_id": settings.telegram_chat_id, "text": chunk})
            resp.raise_for_status()
    return True
