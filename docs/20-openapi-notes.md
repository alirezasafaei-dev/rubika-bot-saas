# OpenAPI Notes

## نسخه
OpenAPI: 3.0.3

## نحوه استفاده

### Swagger Editor
فایل `openapi.yaml` را در Swagger Editor باز کنید:
https://editor.swagger.io/

### Swagger UI
می‌توانید در بک‌اند خود mount کنید:
- FastAPI: `/docs`
- NestJS Swagger: `/api/docs`

### Postman
Import -> File -> `openapi.yaml`

---

## نکات پیاده‌سازی
- `servers.url` را در محیط production به دامنه واقعی تغییر دهید
- اگر auth با cookie بود، security scheme باید اصلاح شود
- اگر Rubika webhook امضای اختصاصی دارد، header validation دقیق‌تر شود

---
