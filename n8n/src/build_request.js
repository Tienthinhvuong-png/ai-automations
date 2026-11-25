// Node "Chuẩn bị yêu cầu Claude": nhận sản phẩm (từ webhook hoặc chạy thử), tạo nội dung gửi Claude API.
// ==== Sửa thông tin thương hiệu ở đây ====
const BRAND_NAME = 'Cửa hàng của anh';
const BRAND_VOICE = "thân thiện, gần gũi, chuyên nghiệp, xưng 'mình' và gọi khách là 'bạn'";
const MODEL = 'claude-opus-5-5';
const EFFORT = 'medium'; // low | medium | high

const SAMPLE = {
  name: 'Bình giữ nhiệt inox 500ml',
  description: 'Inox 304, giữ nóng và lạnh lâu, nắp chống tràn, nhỏ gọn bỏ vừa túi xách',
  price: '189.000đ',
  promotion: 'Mua 2 tặng 1 túi vải đến hết tháng 12',
  target_customer: 'Dân văn phòng, sinh viên',
  link: '',
};

const SYSTEM = `Bạn là chuyên viên content marketing cho thương hiệu "${BRAND_NAME}" tại Việt Nam.
Giọng văn: ${BRAND_VOICE}.

Viết bằng tiếng Việt có dấu, tự nhiên như người bán hàng thật, không sáo rỗng.
Chỉ dùng thông tin có trong mô tả sản phẩm. Không bịa thông số, cam kết, chứng nhận hay giá.
Không dùng từ ngữ bị cấm trong quảng cáo như "tốt nhất", "số 1", "chữa khỏi" nếu không có căn cứ.

Mỗi lần nhận một sản phẩm, bạn tạo:
- 2 bài Facebook theo 2 góc khác nhau (ví dụ: nỗi đau của khách và lợi ích nổi bật). Mỗi bài 80 đến 150 chữ, có tiêu đề, lời kêu gọi hành động và 3 đến 5 hashtag.
- Nội dung YouTube: tiêu đề dưới 70 ký tự có từ khóa chính, phần mô tả 100 đến 200 chữ, 5 đến 10 thẻ tag, và kịch bản YouTube Shorts 30 đến 45 giây gồm câu mở đầu giữ chân người xem trong 3 giây đầu và 3 đến 6 cảnh ngắn.
- 1 tin nhắn Zalo gửi khách cũ, dưới 60 chữ, lịch sự, có lời mời rõ ràng.`;

const str = { type: 'string' };
const strList = { type: 'array', items: str };
const obj = (properties) => ({
  type: 'object',
  properties,
  required: Object.keys(properties),
  additionalProperties: false,
});

const SCHEMA = obj({
  facebook_posts: {
    type: 'array',
    items: obj({ headline: str, body: str, call_to_action: str, hashtags: strList }),
  },
  youtube: obj({
    title: str,
    description: str,
    tags: strList,
    shorts_script: obj({ hook: str, scenes: strList }),
  }),
  zalo_message: str,
});

const FIELDS = [
  ['name', 'Sản phẩm'],
  ['description', 'Mô tả'],
  ['price', 'Giá'],
  ['promotion', 'Khuyến mãi'],
  ['target_customer', 'Khách hàng mục tiêu'],
  ['link', 'Link'],
];

return $input.all().map((item) => {
  // Webhook đặt dữ liệu trong body; chạy thử bằng tay thì dùng sản phẩm mẫu.
  const input = item.json.body ?? item.json;
  const product = input && input.name ? input : SAMPLE;
  if (!product.description) throw new Error(`Thiếu mô tả cho sản phẩm "${product.name}"`);

  const userText = FIELDS.filter(([k]) => product[k])
    .map(([k, label]) => `${label}: ${product[k]}`)
    .join('\n');

  return {
    json: {
      product,
      request: {
        model: MODEL,
        max_tokens: 16000,
        system: SYSTEM,
        messages: [{ role: 'user', content: userText }],
        output_config: { effort: EFFORT, format: { type: 'json_schema', schema: SCHEMA } },
        // Nếu model chính từ chối, API tự chạy lại trên model dự phòng phù hợp.
        fallbacks: 'default',
      },
    },
  };
});
