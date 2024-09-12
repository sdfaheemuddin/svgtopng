from flask import Flask, request, send_file
import cairosvg
from io import BytesIO
import os  # Import the os module

app = Flask(__name__)

# Health check route to verify the app is running
@app.route('/', methods=['GET'])
def home():
    return "SVG to PNG Converter is running!", 200

# Route for converting SVG to PNG
@app.route('/convert', methods=['GET', 'POST'])
def convert_svg_to_png():
    try:
        # Extract SVG code from request args (GET) or form data (POST)
        if request.method == 'GET':
            svg_code = request.args.get('svg')
        elif request.method == 'POST':
            svg_code = request.form.get('svg')
        
        if not svg_code:
            return "SVG code not provided", 400

        # Convert SVG to PNG using cairosvg
        output = BytesIO()
        cairosvg.svg2png(bytestring=svg_code.encode('utf-8'), write_to=output)

        # Send the converted PNG as a downloadable file
        output.seek(0)
        return send_file(output, mimetype='image/png', as_attachment=True, download_name="image.png")
    
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # Run the app on 0.0.0.0 to make it publicly accessible
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
