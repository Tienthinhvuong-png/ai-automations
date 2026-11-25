"""Webhook để hệ thống khác (n8n, Google Sheets Apps Script, Zapier...) gọi vào.

Chạy:  uvicorn app.api:app --port 8000
Gọi:   POST /content/generate  với JSON là thông tin sản phẩm.
"""

from fastapi import FastAPI, HTTPException

from app.config import settings
from app.content.generator import ContentGenerator, ContentRefused
from app.content.schemas import MarketingPack, Product
from app.outputs.storage import save_pack, to_markdown
from app.outputs.telegram import send_for_review

app = FastAPI(title="AI Automations: nội dung marketing")
_generator: ContentGenerator | None = None


def get_generator() -> ContentGenerator:
    global _generator
    if _generator is None:
        _generator = ContentGenerator()
    return _generator


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/content/generate", response_model=MarketingPack)
def generate(product: Product) -> MarketingPack:
    try:
        pack = get_generator().generate(product)
    except ContentRefused as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    save_pack(product, pack, settings.output_dir)
    send_for_review(to_markdown(product, pack), settings)
    return pack
