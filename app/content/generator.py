"""Gọi Claude để tạo bộ nội dung marketing cho một sản phẩm."""

import logging

import anthropic

from app.config import Settings, settings as default_settings
from app.content.prompts import system_prompt, user_prompt
from app.content.schemas import MarketingPack, Product

log = logging.getLogger(__name__)


class ContentRefused(RuntimeError):
    """Claude từ chối viết nội dung này (ví dụ sản phẩm vi phạm chính sách)."""


class ContentGenerator:
    def __init__(self, client: anthropic.Anthropic | None = None, settings: Settings = default_settings):
        # Anthropic() tự đọc ANTHROPIC_API_KEY từ môi trường.
        self.client = client or anthropic.Anthropic()
        self.settings = settings

    def generate(self, product: Product) -> MarketingPack:
        response = self.client.beta.messages.parse(
            model=self.settings.claude_model,
            max_tokens=16000,
            system=system_prompt(self.settings.brand_name, self.settings.brand_voice),
            messages=[{"role": "user", "content": user_prompt(product)}],
            output_format=MarketingPack,
            output_config={"effort": self.settings.claude_effort},
            # Nếu model chính từ chối, API tự chạy lại trên model dự phòng phù hợp.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )

        if response.stop_reason == "refusal":
            raise ContentRefused(f"Claude từ chối tạo nội dung cho '{product.name}'")
        if response.stop_reason == "max_tokens" or response.parsed_output is None:
            raise RuntimeError(f"Kết quả cho '{product.name}' bị cắt ngang hoặc không đọc được")

        log.info(
            "Đã tạo nội dung cho %s (model %s, %s token vào, %s token ra)",
            product.name,
            response.model,
            response.usage.input_tokens,
            response.usage.output_tokens,
        )
        return response.parsed_output
