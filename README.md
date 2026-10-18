# Website tour Mèo về núi

Website tĩnh giới thiệu 4 tour Quảng Trị của Mèo về núi. Chạy miễn phí trên Cloudflare Pages, không cần máy chủ hay cơ sở dữ liệu.

## Các trang

| Trang | Đường dẫn |
|---|---|
| Trang chủ | `/` |
| Khe Sanh 2 ngày 1 đêm | `/tour/khe-sanh-2n1d/` |
| Quảng Trị 3 ngày 2 đêm | `/tour/quang-tri-3n2d/` |
| Thác Tà Puồng 1 ngày | `/tour/ta-puong-1-ngay/` |
| Quảng Trị 1 ngày theo dòng lịch sử | `/tour/quang-tri-1-ngay/` |
| Cách đặt tour và hoàn huỷ | `/dat-tour/` |

Mỗi tour có link riêng để gửi khách. Khi dán link vào Zalo, Messenger sẽ hiện ảnh bìa và tên tour.

## Thư mục

- `src/tours.json`: toàn bộ chữ, giá, lịch trình, danh sách video. Sửa nội dung chỉ cần sửa file này.
- `src/img/`: ảnh đã nén. `src/img/og/` là ảnh xem trước khi chia sẻ link (1200x630).
- `src/img/video/<id>.jpg`: ảnh bìa video TikTok, tên file là mã số video.
- `src/assets/`: giao diện (`style.css`) và tương tác (`main.js`).
- `build.py`: dựng website từ `src/` ra `dist/`.
- `dist/`: bản hoàn chỉnh để đưa lên mạng. Không sửa tay trong này, mỗi lần build sẽ ghi đè.

## Sửa nội dung

1. Mở `src/tours.json`, sửa giá, giờ, chữ. Chữ nằm giữa `**...**` sẽ in đậm.
2. Chạy:

```bash
python3 build.py
```

3. Commit và push lên nhánh `main`. GitHub tự dựng lại web và cập nhật sau khoảng 1 phút.

**Thêm video TikTok:** lấy mã số trong link video (dãy số sau `/video/`), thêm vào mục `videos` (mã và tiêu đề), rồi thêm mã vào danh sách `videos` của tour. Ảnh bìa đặt ở `src/img/video/<mã>.jpg`.

**Thêm tour mới:** copy một khối tour trong `tours`, đổi `slug` (đường dẫn), tên, ảnh, lịch trình. Thêm ảnh OG `src/img/og/<slug>.jpg`.

## Đang chạy ở đâu

- Cloudflare Pages (link chính gửi khách): https://meovenui.pages.dev/ , dự án `meovenui` trong tài khoản Cloudflare lbph.work@gmail.com.
- GitHub Pages (bản dự phòng): https://lbphwork-cloud.github.io/meovenui/

Cập nhật bản Cloudflare sau khi sửa nội dung:

```bash
python3 build.py && npx wrangler@4 pages deploy dist --project-name meovenui --branch main
```

File `.github/workflows/pages.yml` tự chạy `build.py` mỗi lần push lên `main`, với `SITE_URL` và `BASE_PATH` khớp đường dẫn `/meovenui/`.

## Chuyển sang Cloudflare Pages (miễn phí)

**Cách 0, nối thẳng với repo GitHub này (nên dùng):** trong Cloudflare, Workers & Pages, Create, Pages, Connect to Git, chọn repo `meovenui`. Build command: `python3 build.py`, Build output directory: `dist`. Không đặt `BASE_PATH` vì Cloudflare chạy web ở thư mục gốc. Sửa `site.url` trong `src/tours.json` thành địa chỉ Cloudflare.

**Cách 1, kéo thả (không cần cài gì):**

1. Tạo tài khoản miễn phí ở dash.cloudflare.com.
2. Vào Workers & Pages, chọn Create, tab Pages, chọn Upload assets.
3. Đặt tên dự án `meovenui` để có địa chỉ `meovenui.pages.dev`.
4. Kéo thả thư mục `dist/` (hoặc file `meovenui-dist.zip`) vào, bấm Deploy.
5. Lần sau cập nhật: vào dự án `meovenui`, chọn Create deployment, kéo thả lại `dist/`.

**Cách 2, dòng lệnh:**

```bash
npx wrangler login
```

```bash
npx wrangler pages deploy dist --project-name meovenui
```

Nếu tên `meovenui` đã có người dùng, Cloudflare sẽ báo. Khi đó đổi sang tên khác và sửa `site.url` trong `src/tours.json` cho khớp, rồi build lại, vì ảnh xem trước khi chia sẻ link cần đúng địa chỉ.

## Khi mua tên miền

Trong dự án Pages, vào Custom domains, thêm tên miền và làm theo hướng dẫn trỏ DNS. Sau đó đổi `site.url` trong `src/tours.json` sang tên miền mới, build và đưa lên lại.

## Nguồn nội dung

- File PDF tour Khe Sanh 2N1Đ (Google Drive).
- Canva tour ghép Quảng Trị 3N2Đ dịp 2/9.
- Canva poster tour Tà Puồng 1 ngày và tour Quảng Trị 1 ngày.
- Video và số liệu từ TikTok @meovenui (lấy ngày 18/10/2026).
