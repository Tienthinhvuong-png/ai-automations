"""Luồng đầy đủ: sản phẩm -> Claude viết nội dung -> lưu file -> gửi Telegram duyệt."""

import csv
import logging
from dataclasses import dataclass
from pathlib import Path

from app.config import Settings, settings as default_settings
from app.content.generator import ContentGenerator
from app.content.schemas import Product
from app.outputs.storage import save_pack, to_markdown
from app.outputs.telegram import send_for_review

log = logging.getLogger(__name__)


@dataclass
class Result:
    product: str
    ok: bool
    file: Path | None = None
    error: str = ""


def run_one(product: Product, generator: ContentGenerator, settings: Settings = default_settings) -> Result:
    try:
        pack = generator.generate(product)
        path = save_pack(product, pack, settings.output_dir)
        send_for_review(to_markdown(product, pack), settings)
        return Result(product.name, True, path)
    except Exception as exc:  # một sản phẩm lỗi không làm dừng cả lô
        log.exception("Lỗi khi xử lý %s", product.name)
        return Result(product.name, False, error=str(exc))


def load_products(csv_path: Path) -> list[Product]:
    with csv_path.open(encoding="utf-8-sig") as f:
        return [Product(**{k: (v or "").strip() for k, v in row.items() if k}) for row in csv.DictReader(f)]


def run_batch(csv_path: Path, generator: ContentGenerator | None = None, settings: Settings = default_settings) -> list[Result]:
    generator = generator or ContentGenerator(settings=settings)
    return [run_one(p, generator, settings) for p in load_products(csv_path)]
