"""Dữ liệu đầu vào (sản phẩm) và đầu ra (bộ nội dung marketing)."""

from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    name: str = Field(description="Tên sản phẩm")
    description: str = Field(description="Mô tả ngắn, công dụng, điểm nổi bật")
    price: str = Field(default="", description="Giá bán, ví dụ 299.000đ")
    promotion: str = Field(default="", description="Khuyến mãi đang chạy, nếu có")
    target_customer: str = Field(default="", description="Khách hàng mục tiêu")
    link: str = Field(default="", description="Link mua hàng hoặc Fanpage")


class FacebookPost(BaseModel):
    model_config = ConfigDict(extra="forbid")

    headline: str
    body: str
    call_to_action: str
    hashtags: list[str]


class ShortsScript(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hook: str
    scenes: list[str]


class YouTubeContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str
    tags: list[str]
    shorts_script: ShortsScript


class MarketingPack(BaseModel):
    """Một bộ nội dung cho một sản phẩm, đủ dùng cho 3 kênh."""

    model_config = ConfigDict(extra="forbid")

    facebook_posts: list[FacebookPost]
    youtube: YouTubeContent
    zalo_message: str
