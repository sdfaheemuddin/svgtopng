
from flask import Flask, request, send_file
import cairosvg
from io import BytesIO

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_svg_to_png():
    try:
        # Extract SVG code from the request
        svg_code = request.form.get('svg')
        
        if not svg_code:
            return "SVG code not provided", 400

        # Convert SVG to PNG
        output = BytesIO()
        cairosvg.svg2png(bytestring=svg_code.encode('utf-8'), write_to=output)

        # Send the converted PNG as a downloadable file
        output.seek(0)
        return send_file(output, mimetype='image/png', as_attachment=True, download_name="image.png")
    
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
