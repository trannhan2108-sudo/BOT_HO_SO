# Bot săn mã thẻ nạp game

Bot sử dụng [Telethon](https://docs.telethon.dev/en/latest/) để:

- Đăng nhập bằng tài khoản Telegram cá nhân và theo dõi các channel/group do bạn cấu hình.
- Bắt các chuỗi ký tự khớp với regex (ví dụ mã thẻ gồm 12-16 chữ số) ngay khi xuất hiện.
- Gửi thông báo tới những người dùng đã `/start` bot qua kênh bot Telegram riêng.
- Lưu lại lịch sử các mã vừa săn được để tra cứu bằng lệnh `/history`.

## Cài đặt nhanh

1. Cài gói phụ thuộc:

   ```bash
   pip install -r requirements.txt
   ```

2. Sao chép file `.env.example` thành `.env` và điền các thông tin bắt buộc:

   - `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`: lấy từ [my.telegram.org](https://my.telegram.org/).
   - `TELEGRAM_BOT_TOKEN`: token của bot do BotFather cấp.
   - `TELEGRAM_WATCH_CHANNELS`: danh sách channel/group muốn theo dõi, cách nhau bằng dấu phẩy.

3. Chạy bot:

   ```bash
   python -m telegram_bot.runner
   ```

   Lần đầu chạy Telethon sẽ yêu cầu mã OTP để tạo session cho tài khoản người dùng.

## Các lệnh hỗ trợ (qua bot Telegram)

- `/start`: đăng ký nhận thông báo.
- `/stop`: hủy nhận thông báo.
- `/status`: xem trạng thái hiện tại (kênh đang theo dõi + regex).
- `/history`: xem 10 mã gần nhất.
- `/help`: hiển thị lại danh sách lệnh.

## Tuỳ chỉnh thêm

- Cập nhật biến môi trường `SNIPER_RULES` trong `.env` để bổ sung regex tìm mã.
- Thay đổi `SNIPER_HISTORY_SIZE` để điều chỉnh số lượng bản ghi lịch sử lưu lại.
- Dữ liệu (session, subscribers, history) được lưu tại thư mục `runtime` (có thể đổi bằng `SNIPER_DATA_DIR`).
