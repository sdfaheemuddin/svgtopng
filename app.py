from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
import cairosvg
from rembg import remove, new_session
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import os

app = Flask(__name__)

MAX_IMAGE_BYTES = int(os.environ.get("MAX_IMAGE_BYTES", 5 * 1024 * 1024))
ALLOWED_IMAGE_MIMES = {"image/jpeg", "image/png", "image/webp"}

# Load once and reuse. This avoids reloading the model for every request.
rembg_session = new_session(os.environ.get("REMBG_MODEL", "u2net_human_seg"))


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

        transparent_bytes = remove(input_bytes, session=rembg_session)
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
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
