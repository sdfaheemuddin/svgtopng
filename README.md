# SVG to PNG Converter API - User Guide

This API allows you to convert SVG (Scalable Vector Graphics) files into PNG (Portable Network Graphics) format. You can interact with the API via HTTP requests and receive the converted PNG image in return.

## Features

- Convert SVG to PNG format.
- Supports both `POST` and `GET` methods.
- Returns the converted PNG image as a downloadable file.

## API Endpoints

**Base url:**
```
https://svgtopng.onrender.com
```

### 1. Convert SVG to PNG (POST)

**Endpoint:**

```
POST /convert
```

**Request:**

- **Content-Type**: `application/x-www-form-urlencoded`
- **Body Parameter**:
  - `svg`: Your SVG code (string).

**Example cURL Request:**

```bash
curl -X POST -F 'svg=<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red"/></svg>' https://svgtopng.onrender.com/convert --output image.png
```

### 2. Convert SVG to PNG (GET)

**Endpoint:**

```
GET /convert
```

**Request:**

- **URL Parameter**: `svg` (URL-encoded SVG string).

**Example GET Request:**

```plaintext
https://svgtopng.onrender.com/convert?svg=%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20100%20100%22%3E%3Ccircle%20cx%3D%2250%22%20cy%3D%2250%22%20r%3D%2240%22%20stroke%3D%22black%22%20stroke-width%3D%223%22%20fill%3D%22red%22%2F%3E
```

The API will respond with a downloadable PNG file.

## Example SVG Code:

You can use the following sample SVG code to test the API:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red"/>
</svg>
```

## API Testing via Postman

To quickly test the API, you can use the Postman collection provided below. Click the button to import the collection into Postman:

[![App Platorm](https://run.pstmn.io/button.svg)](https://god.gw.postman.com/run-collection/17577897-86f551f8-c830-43bc-8daf-5466a0a1d6dd?action=collection%2Ffork&source=rip_markdown&collection-url=entityId%3D17577897-86f551f8-c830-43bc-8daf-5466a0a1d6dd%26entityType%3Dcollection%26workspaceId%3De763b87e-66a9-4e15-bad3-22c2ae2e55eb)

---

### Error Handling

- **400 Bad Request**: Occurs if the `svg` parameter is missing or invalid.
- **500 Internal Server Error**: Occurs if there’s an internal issue during the conversion process.
