from flask import Flask, request, send_file, jsonify, g
from werkzeug.utils import secure_filename
import cairosvg
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import json
import logging
import os
import time


app = Flask(__name__)

MAX_IMAGE_BYTES = int(os.environ.get("MAX_IMAGE_BYTES", 5 * 1024 * 1024))
ALLOWED_IMAGE_MIMES = {"image/jpeg", "image/png", "image/webp"}

# Structured request logging. Render sits behind a proxy, so request.remote_addr
# is often an internal address. X-Forwarded-For is logged separately to expose
# the originating client IP when Render provides it.
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("svgtopng")

# Background removal is intentionally lazy-loaded. Loading rembg/ONNX and its
# segmentation model during process startup can exceed Render free-tier memory.
rembg_session = None


def _get_rembg():
    """Import rembg and initialize its model only when background removal is used."""
    global rembg_session
    from rembg import remove, new_session

    if rembg_session is None:
        logger.info("Loading rembg model on first /remove-bg-white request")
        rembg_session = new_session(os.environ.get("REMBG_MODEL", "u2net_human_seg"))

    return remove, rembg_session


def _safe_request_source():
    """Return non-sensitive request metadata useful for identifying callers."""
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.remote_addr

    return {
        "event": "request",
        "method": request.method,
        "path": request.path,
        "query_present": bool(request.query_string),
        "status_host": request.host,
        "client_ip": client_ip,
        "remote_addr": request.remote_addr,
        "x_forwarded_for": forwarded_for or None,
        "x_real_ip": request.headers.get("X-Real-IP"),
        "x_forwarded_proto": request.headers.get("X-Forwarded-Proto"),
        "user_agent": request.headers.get("User-Agent"),
        "referer": request.headers.get("Referer"),
        "origin": request.headers.get("Origin"),
        # Optional caller-supplied tag. Add X-Client-Name in apps/scripts that
        # call this API to identify them explicitly in logs.
        "client_name": request.headers.get("X-Client-Name"),
        "content_type": request.content_type,
        "content_length": request.content_length,
    }


@app.before_request
def log_request_start():
    g.request_started_at = time.perf_counter()
    logger.info(json.dumps(_safe_request_source(), separators=(",", ":")))


@app.after_request
def log_request_end(response):
    started_at = getattr(g, "request_started_at", None)
    duration_ms = (
        round((time.perf_counter() - started_at) * 1000, 2)
        if started_at is not None
        else None
    )

    logger.info(
        json.dumps(
            {
                "event": "response",
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
            separators=(",", ":"),
        )
    )
    return response


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "running",
        "service": "SVG to PNG and image background API",
        "endpoints": [
            "GET/POST /convert",
            "POST /remove-bg-white"
        ]
    }), 200


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200


@app.route('/convert', methods=['GET', 'POST'])
def convert_svg_to_png():
    try:
        if request.method == 'GET':
            svg_code = request.args.get('svg')
        else:
            svg_code = request.form.get('svg')

        if not svg_code:
            return "SVG code not provided", 400

        output = BytesIO()
        cairosvg.svg2png(bytestring=svg_code.encode('utf-8'), write_to=output)
        output.seek(0)
        return send_file(output, mimetype='image/png', as_attachment=True, download_name="image.png")

    except Exception as e:
        logger.exception("SVG conversion failed")
        return str(e), 500


@app.route('/remove-bg-white', methods=['POST'])
def remove_background_white():
    try:
        uploaded = request.files.get('file')
        if not uploaded:
            return jsonify({"error": "Image file not provided. Upload using multipart/form-data field name 'file'."}), 400

        filename = secure_filename(uploaded.filename or "image")
        content_type = uploaded.mimetype or ""
        if content_type not in ALLOWED_IMAGE_MIMES:
            return jsonify({"error": "Unsupported image type. Use JPG, PNG, or WebP."}), 400

        input_bytes = uploaded.read(MAX_IMAGE_BYTES + 1)
        if len(input_bytes) > MAX_IMAGE_BYTES:
            return jsonify({"error": f"Image too large. Maximum allowed size is {MAX_IMAGE_BYTES // (1024 * 1024)} MB."}), 413

        try:
            Image.open(BytesIO(input_bytes)).verify()
        except (UnidentifiedImageError, OSError):
            return jsonify({"error": "Invalid image file."}), 400

        remove, session = _get_rembg()
        transparent_bytes = remove(input_bytes, session=session)
        transparent = Image.open(BytesIO(transparent_bytes)).convert("RGBA")

        white = Image.new("RGBA", transparent.size, "WHITE")
        white.alpha_composite(transparent)

        output = BytesIO()
        white.convert("RGB").save(output, format="JPEG", quality=92, optimize=True)
        output.seek(0)

        base_name = os.path.splitext(filename)[0] or "image"
        return send_file(
            output,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name=f"{base_name}_white_bg.jpg"
        )

    except Exception as e:
        logger.exception("Background removal failed")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
        host='0.0.0.0',
        port=int(os.environ.get("PORT", 5000)),
    )
