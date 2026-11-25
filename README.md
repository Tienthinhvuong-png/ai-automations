# AI Automations: tạo nội dung marketing

Luồng tự động đầu tiên: anh đưa thông tin sản phẩm, Claude viết sẵn nội dung cho 3 kênh:

- **Facebook:** 2 bài theo 2 góc khác nhau, có tiêu đề, lời kêu gọi và hashtag.
- **YouTube:** tiêu đề, mô tả, thẻ tag và kịch bản YouTube Shorts.
- **Zalo:** 1 tin nhắn gửi khách cũ.

```
Sản phẩm (webhook hoặc chạy thử) -> Claude viết nội dung -> trả JSON + bản xem nhanh để duyệt
```

Có 2 cách chạy, cùng một lời dặn cho AI. **Cách chính là n8n.** Phần Python giữ lại làm phương án dự phòng.

## 1. Chạy bằng n8n (cách chính)

### Nhập workflow

1. Trong n8n, chọn **Workflows > Import from File**, chọn file `n8n/marketing-content.json`.
2. Tạo khóa Claude API tại https://platform.claude.com (mục API Keys).
3. Mở node **Gọi Claude API**, ở ô Credential chọn **Create new credential** loại **Header Auth**:
   - Name: `x-api-key`
   - Value: khóa API vừa tạo
4. Mở node **Chuẩn bị yêu cầu Claude**, sửa `BRAND_NAME` và `BRAND_VOICE` ở đầu đoạn mã cho đúng thương hiệu của anh.

### Chạy thử

Bấm **Test workflow**. Workflow dùng sản phẩm mẫu (bình giữ nhiệt). Kết quả ở node **Đọc kết quả**, trường `preview` là bản dễ đọc để duyệt.

### Gọi từ nơi khác

Bật workflow (Active), rồi gửi sản phẩm vào webhook:

```bash
curl -X POST https://<n8n-cua-anh>/webhook/marketing-content \
  -H "Content-Type: application/json" \
  -d '{"name": "Bình giữ nhiệt", "description": "Inox 304, giữ nhiệt lâu", "price": "189.000đ", "promotion": "", "target_customer": "Dân văn phòng", "link": ""}'
```

Chỉ `name` và `description` là bắt buộc. Webhook trả về JSON gồm `facebook_posts`, `youtube`, `zalo_message` và `preview`.

### Sửa workflow

Mã của 2 node Code nằm trong `n8n/src/`. Có thể sửa trực tiếp trong n8n, hoặc sửa file trong `src/` rồi chạy `python n8n/build_workflow.py` để tạo lại file nhập.

## 2. Chạy bằng Python (dự phòng)

Cần Python 3.11 trở lên.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # điền ANTHROPIC_API_KEY và thông tin thương hiệu
python -m app.cli data/products.csv
```

Kết quả nằm trong `output/`: mỗi sản phẩm có một file `.md` để đọc và một file `.json`. Có thể chạy dạng webhook bằng `uvicorn app.api:app --port 8000`, và gửi bản nháp qua Telegram nếu điền `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.

Chạy kiểm thử (không tốn tiền API): `pytest`

## Cấu trúc

| Đường dẫn | Vai trò |
| --- | --- |
| `n8n/marketing-content.json` | Workflow n8n để nhập |
| `n8n/src/` | Mã của các node Code trong workflow |
| `app/content/` | Bản Python: lời dặn cho AI, định dạng dữ liệu, gọi Claude |
| `app/outputs/` | Bản Python: lưu file, gửi Telegram |
| `tests/` | Kiểm thử bản Python |

## Ghi chú kỹ thuật

- Model `claude-opus-5-5`, mức suy nghĩ `medium`.
- Kết quả được ép đúng cấu trúc JSON (structured outputs), nên các bước sau luôn đọc được.
- Đã bật tự chuyển sang model dự phòng nếu model chính từ chối một yêu cầu.
- Lời dặn cho AI có ở 2 nơi: `n8n/src/build_request.js` và `app/content/prompts.py`. Sửa một nơi thì nhớ sửa nơi kia.

## Bước tiếp theo

- Thêm bước duyệt (ví dụ qua Zalo hoặc Telegram) rồi tự đăng lên Fanpage, gửi tin Zalo OA, đăng mô tả lên YouTube.
- Nhận danh sách sản phẩm từ Google Sheets thay vì webhook.
