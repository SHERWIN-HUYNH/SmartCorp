# Tesseract Docker Quick Usage (SmartCorp server/app)

Muc tieu: chay Tesseract bang Docker, khong can cai local va khong can set PATH tren may dev.

## 1) Build image

```bash
docker compose -f docker-compose.tesseract.yml build
```

## 2) Kiem tra version

```bash
docker compose -f docker-compose.tesseract.yml run --rm tesseract --version
```

## 3) OCR file anh

Vi du OCR `sample.png` va xuat `sample_out.txt`:

```bash
docker compose -f docker-compose.tesseract.yml run --rm tesseract sample.png sample_out -l eng
```

Tieng Viet:

```bash
docker compose -f docker-compose.tesseract.yml run --rm tesseract sample.png sample_out -l vie
```

## 4) Luu y

- Chay lenh trong thu muc `SmartCorp/server/app`.
- File output `.txt` duoc tao ngay trong thu muc dang mount vao container.
- Tesseract OCR tot nhat voi anh (png/jpg/tif). Neu input la PDF, nen convert PDF thanh anh truoc.
