"""Kiểm thử không gọi API thật: thay Claude bằng một client giả."""

from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

import app.api as api
from app.config import Settings
from app.content.generator import ContentGenerator, ContentRefused
from app.content.schemas import FacebookPost, MarketingPack, Product, ShortsScript, YouTubeContent
from app.outputs.storage import slugify
from app.pipeline import run_batch

PACK = MarketingPack(
    facebook_posts=[FacebookPost(headline="Tiêu đề", body="Nội dung", call_to_action="Nhắn ngay", hashtags=["#a"])],
    youtube=YouTubeContent(title="T", description="D", tags=["a"], shorts_script=ShortsScript(hook="Mở đầu", scenes=["Cảnh 1"])),
    zalo_message="Chào bạn",
)


class FakeClient:
    def __init__(self, stop_reason="end_turn", parsed=PACK):
        self.calls = []
        response = SimpleNamespace(
            stop_reason=stop_reason,
            parsed_output=parsed,
            model="claude-opus-5-5",
            usage=SimpleNamespace(input_tokens=1, output_tokens=1),
        )
        self.beta = SimpleNamespace(messages=SimpleNamespace(parse=lambda **kw: self.calls.append(kw) or response))


def settings(tmp_path: Path) -> Settings:
    return Settings(output_dir=tmp_path / "out", telegram_bot_token="", telegram_chat_id="")


def test_generate_sends_expected_request(tmp_path):
    client = FakeClient()
    gen = ContentGenerator(client=client, settings=settings(tmp_path))
    assert gen.generate(Product(name="Bình", description="Inox")) == PACK
    call = client.calls[0]
    assert call["model"] == "claude-opus-5-5"
    assert call["output_format"] is MarketingPack
    assert call["fallbacks"] == "default"
    assert "Bình" in call["messages"][0]["content"]


def test_refusal_raises(tmp_path):
    gen = ContentGenerator(client=FakeClient(stop_reason="refusal", parsed=None), settings=settings(tmp_path))
    try:
        gen.generate(Product(name="X", description="Y"))
    except ContentRefused:
        return
    raise AssertionError("expected ContentRefused")


def test_batch_writes_files(tmp_path):
    csv_path = Path(__file__).parent.parent / "data" / "products.csv"
    s = settings(tmp_path)
    results = run_batch(csv_path, ContentGenerator(client=FakeClient(), settings=s), s)
    assert len(results) == 1 and results[0].ok
    md = results[0].file.read_text(encoding="utf-8")
    assert "Bình giữ nhiệt" in md and "Tin nhắn Zalo" in md and "YouTube: T" in md
    assert results[0].file.with_suffix(".json").exists()


def test_api_endpoint(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "settings", settings(tmp_path))
    monkeypatch.setattr(api, "_generator", ContentGenerator(client=FakeClient(), settings=settings(tmp_path)))
    resp = TestClient(api.app).post("/content/generate", json={"name": "Bình", "description": "Inox"})
    assert resp.status_code == 200
    assert resp.json()["zalo_message"] == "Chào bạn"


def test_slugify_vietnamese():
    assert slugify("Bình giữ nhiệt Đỏ 500ml") == "binh-giu-nhiet-do-500ml"
