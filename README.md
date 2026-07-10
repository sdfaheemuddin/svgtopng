# SVG to PNG Converter API - User Guide

This API allows you to convert SVG files into PNG images and process uploaded photos by removing the background and placing the result on a white background.

## Features

- Convert SVG to PNG format.
- Supports SVG conversion using both `POST` and `GET` methods.
- Remove image background and return a white-background JPG.
- Designed for use from other apps such as the SIR Family Form Tool.

## API Endpoints

**Base url:**

```text
https://svgtopng.onrender.com
```

---

## 1. Convert SVG to PNG - POST

**Endpoint:**

```text
POST /convert
```

**Request:**

- **Content-Type**: `application/x-www-form-urlencoded` or `multipart/form-data`
- **Body Parameter**:
  - `svg`: SVG code as a string

**Example cURL Request:**

```bash
curl -X POST \
  -F 'svg=<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red"/></svg>' \
  https://svgtopng.onrender.com/convert \
  --output image.png
```

---

## 2. Convert SVG to PNG - GET

**Endpoint:**

```text
GET /convert
```

**Request:**

- **URL Parameter**: `svg`, URL-encoded SVG string

**Example GET Request:**

```text
https://svgtopng.onrender.com/convert?svg=%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%20100%20100%22%3E%20%3Ccircle%20cx=%2250%22%20cy=%2250%22%20r=%2240%22%20stroke=%22black%22%20stroke-width=%223%22%20fill=%22red%22/%3E%20%3C/svg%3E
```

[Click here](https://svgtopng.onrender.com/convert?svg=%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%20100%20100%22%3E%20%3Ccircle%20cx=%2250%22%20cy=%2250%22%20r=%2240%22%20stroke=%22black%22%20stroke-width=%223%22%20fill=%22red%22/%3E%20%3C/svg%3E)

The API will respond with a downloadable PNG file.

---

## 3. Remove Background and Add White Background

**Endpoint:**

```text
POST /remove-bg-white
```

**Request:**

- **Content-Type**: `multipart/form-data`
- **Body Parameter**:
  - `file`: JPG, PNG, or WebP image

**Example cURL Request:**

```bash
curl -X POST \
  -F "file=@photo.jpg" \
  https://svgtopng.onrender.com/remove-bg-white \
  --output photo_white_bg.jpg
```

**Response:**

```text
image/jpeg
```

The API removes the background using `rembg`, composites the result onto a white background, and returns a JPG file.

---

## Health Check

```text
GET /health
```

Expected response:

```json
{"status":"ok"}
```

---

## Deployment Notes

For Render, this repo includes `render.yaml`.

Recommended start command:

```bash
gunicorn app:app --timeout 180 --workers 1
```

The first background-removal request may be slow because the `rembg` model needs to load/download.

Environment variables:

| Variable | Default | Purpose |
|---|---:|---|
| `REMBG_MODEL` | `u2net_human_seg` | Background-removal model |
| `MAX_IMAGE_BYTES` | `5242880` | Max uploaded image size in bytes |

---

## Error Handling

- **400 Bad Request**: Missing SVG/image, unsupported file type, or invalid image.
- **413 Payload Too Large**: Image is larger than the configured limit.
- **500 Internal Server Error**: Internal conversion or background-removal issue.

## Privacy Note

This API processes uploaded images in memory and returns the processed output. It does not intentionally store uploaded images.
