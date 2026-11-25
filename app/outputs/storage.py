"""Lưu bản nháp ra file: JSON để máy đọc, Markdown để người đọc và duyệt."""

import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

from app.content.schemas import MarketingPack, Product


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower() or "san-pham"


def to_markdown(product: Product, pack: MarketingPack) -> str:
    parts = [f"# Nội dung marketing: {product.name}", ""]
    for i, post in enumerate(pack.facebook_posts, 1):
        parts += [
            f"## Facebook, bài {i}: {post.headline}",
            "",
            post.body,
            "",
            f"**{post.call_to_action}**",
            "",
            " ".join(post.hashtags),
            "",
        ]
    yt = pack.youtube
    parts += [f"## YouTube: {yt.title}", "", yt.description, "", f"**Tag:** {', '.join(yt.tags)}", ""]
    parts += ["### Kịch bản Shorts", "", f"**Mở đầu:** {yt.shorts_script.hook}", ""]
    parts += [f"{i}. {scene}" for i, scene in enumerate(yt.shorts_script.scenes, 1)]
    parts += [""]
    parts += ["## Tin nhắn Zalo", "", pack.zalo_message, ""]
    return "\n".join(parts)


def save_pack(product: Product, pack: MarketingPack, output_dir: Path) -> Path:
    """Ghi 2 file (.json và .md), trả về đường dẫn file .md."""
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{datetime.now():%Y%m%d-%H%M%S}-{slugify(product.name)}"
    data = {"product": product.model_dump(), "content": pack.model_dump()}
    (output_dir / f"{stem}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path = output_dir / f"{stem}.md"
    md_path.write_text(to_markdown(product, pack), encoding="utf-8")
    return md_path
