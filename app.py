from flask import Flask, request, jsonify
from utils import process_youtube_link
from dotenv import load_dotenv
import os

# .env dosyasını yükle
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/google-tts-key.json"

app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Lingroot Transcribe API is running!"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        data = request.get_json()
        youtube_url = data.get("url")
        voice = data.get("voice", "en-US-Wavenet-D")

        if not youtube_url:
            return jsonify({"error": "YouTube URL is required"}), 400

        result = process_youtube_link(youtube_url, voice)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
