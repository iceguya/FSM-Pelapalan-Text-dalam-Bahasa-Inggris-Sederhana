from flask import Flask, render_template, request, send_from_directory
from gtts import gTTS
import os
import requests
import uuid

app = Flask(__name__)
AUDIO_FOLDER = "static/audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    result = {}
    if request.method == "POST":
        word = request.form["word"].strip().lower()
        result["word"] = word.upper()
        result["spelling"] = [c.upper() for c in word]

        # Pelafalan dan arti dari API
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            response = requests.get(url)
            data = response.json()[0]
            # IPA
            ipa = ""
            for p in data.get("phonetics", []):
                if "text" in p:
                    ipa = p["text"]
                    break
            result["ipa"] = ipa
            # Arti
            result["meaning"] = data["meanings"][0]["definitions"][0]["definition"]
        except:
            result["ipa"] = "N/A"
            result["meaning"] = "Tidak ditemukan."

        # Buat audio
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_FOLDER, filename)
        tts = gTTS(text=word, lang='en')
        tts.save(filepath)
        result["audio"] = filename

    return render_template("index.html", result=result)

@app.route("/static/audio/<filename>")
def serve_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
