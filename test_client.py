"""Simple local test client for the SVG to PNG and background-removal API.

Usage:
  1. Start the Flask app in one terminal:
       python app.py

  2. Put a test image at:
       test-images/photo.jpg

  3. Run this script in another terminal:
       python test_client.py

Outputs:
  - test-images/white-bg.jpg
  - test-images/test-svg.png
"""

from pathlib import Path
import sys

import requests


BASE_URL = "http://localhost:5000"
TEST_DIR = Path("test-images")
INPUT_IMAGE = TEST_DIR / "photo.jpg"
OUTPUT_IMAGE = TEST_DIR / "white-bg.jpg"
OUTPUT_SVG_PNG = TEST_DIR / "test-svg.png"
TIMEOUT_SECONDS = 180


SAMPLE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="white"/>
  <circle cx="50" cy="50" r="40" fill="red" stroke="black" stroke-width="3"/>
</svg>"""


def test_health() -> None:
    response = requests.get(f"{BASE_URL}/", timeout=30)
    response.raise_for_status()
    print("Health check OK:", response.text[:120])


def test_svg_to_png() -> None:
    TEST_DIR.mkdir(exist_ok=True)
    response = requests.post(
        f"{BASE_URL}/convert",
        data={"svg": SAMPLE_SVG},
        timeout=60,
    )
    response.raise_for_status()
    OUTPUT_SVG_PNG.write_bytes(response.content)
    print(f"SVG conversion OK: {OUTPUT_SVG_PNG}")


def test_remove_bg_white() -> None:
    if not INPUT_IMAGE.exists():
        raise FileNotFoundError(
            f"Test image not found: {INPUT_IMAGE}\n"
            "Create the folder 'test-images' and place a photo named 'photo.jpg' inside it."
        )

    with INPUT_IMAGE.open("rb") as file_obj:
        response = requests.post(
            f"{BASE_URL}/remove-bg-white",
            files={"file": (INPUT_IMAGE.name, file_obj, "image/jpeg")},
            timeout=TIMEOUT_SECONDS,
        )

    response.raise_for_status()
    OUTPUT_IMAGE.write_bytes(response.content)
    print(f"Background removal OK: {OUTPUT_IMAGE}")


def main() -> int:
    try:
        test_health()
        test_svg_to_png()
        test_remove_bg_white()
    except requests.ConnectionError:
        print("Could not connect to the API. Start it first with: python app.py", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Test failed: {exc}", file=sys.stderr)
        return 1

    print("All tests completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
