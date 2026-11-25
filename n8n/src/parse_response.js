// Node "Đọc kết quả": lấy JSON nội dung từ phản hồi Claude, kèm bản xem nhanh để duyệt.
const products = $('Chuẩn bị yêu cầu Claude').all();

return $input.all().map((item, i) => {
  const res = item.json;
  const product = products[i]?.json.product ?? {};

  if (res.stop_reason === 'refusal') {
    throw new Error(`Claude từ chối tạo nội dung cho "${product.name}"`);
  }
  if (res.stop_reason === 'max_tokens') {
    throw new Error(`Kết quả cho "${product.name}" bị cắt ngang, hãy tăng max_tokens`);
  }
  const text = (res.content || []).find((b) => b.type === 'text')?.text;
  if (!text) throw new Error('Phản hồi của Claude không có nội dung');
  const content = JSON.parse(text);

  const fb = content.facebook_posts
    .map((p, n) => `FACEBOOK ${n + 1}: ${p.headline}\n${p.body}\n${p.call_to_action}\n${p.hashtags.join(' ')}`)
    .join('\n\n');
  const yt = content.youtube;
  const preview = [
    `NỘI DUNG CHO: ${product.name}`,
    fb,
    `YOUTUBE: ${yt.title}\n${yt.description}\nTag: ${yt.tags.join(', ')}`,
    `SHORTS:\nMở đầu: ${yt.shorts_script.hook}\n${yt.shorts_script.scenes.map((s, n) => `${n + 1}. ${s}`).join('\n')}`,
    `ZALO: ${content.zalo_message}`,
  ].join('\n\n');

  return {
    json: {
      product: product.name,
      created_at: new Date().toISOString(),
      model: res.model,
      ...content,
      preview,
    },
  };
});
