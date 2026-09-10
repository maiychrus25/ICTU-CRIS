# ICTU-CRIS frontend

Giao diện Next.js cho hệ thống thông tin nghiên cứu ICTU-CRIS.

## Phát triển với backend

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8001 npm run dev
```

## Phát triển bằng dữ liệu mẫu

```bash
NEXT_PUBLIC_MOCK=1 npm run dev
```

## Xuất bản tĩnh

```bash
npm run build
```

Kết quả nằm trong thư mục `out/` để FastAPI phục vụ tại `/`.
