import os
import uuid
import subprocess
import whisper
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from tts_engine import generate_google_tts
from google.cloud import texttospeech

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def download_audio(youtube_url):
    unique_id = str(uuid.uuid4())
    filename = f"{unique_id}.mp3"
    subprocess.run([
        "yt-dlp",
        "-x", "--audio-format", "mp3",
        "-o", filename,
        youtube_url
    ], check=True)
    return filename

def transcribe_audio(path):
    model = whisper.load_model("base")
    result = model.transcribe(path, language="tr")
    return result["text"]

def translate_to_english(text):
    prompt = f"""Translate the following Turkish speech transcript into fluent, natural spoken English suitable for audio narration. 
Keep the structure of paragraphs and don't summarize or rephrase. Translate sentence by sentence, keeping meaning intact.

TURKISH TEXT:
{text}
"""
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def process_youtube_link(youtube_url, voice_name):
    audio_path = download_audio(youtube_url)
    turkish_text = transcribe_audio(audio_path)
    english_text = translate_to_english(turkish_text)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("output/audio", exist_ok=True)
    os.makedirs("output/transcripts", exist_ok=True)

    audio_output_path = f"output/audio/{timestamp}_output.mp3"
    transcript_output_path = f"output/transcripts/{timestamp}_output.txt"

    generate_google_tts(english_text, voice_name=voice_name, output_path=audio_output_path)

    with open(transcript_output_path, "w", encoding="utf-8") as f:
        f.write(english_text)

    return {
        "transcript": english_text,
        "audio_url": audio_output_path.replace("\\", "/"),
        "transcript_file": transcript_output_path.replace("\\", "/")
    }

def list_google_voices(language_code="en-US"):
    client = texttospeech.TextToSpeechClient()
    response = client.list_voices()

    filtered = [v for v in response.voices if language_code in v.language_codes]

    print("\n🔈 Kullanılabilir Google TTS sesleri:\n")
    for i, voice in enumerate(filtered):
        gender = voice.ssml_gender.name.title()
        print(f"{i + 1}. {voice.name} ({gender})")

    while True:
        try:
            choice = int(input("\n🎙️ Kullanmak istediğiniz ses numarasını girin: ")) - 1
            selected_voice = filtered[choice].name
            print(f"\n✅ Seçilen ses: {selected_voice}")
            return selected_voice
        except (IndexError, ValueError):
            print("⛔ Geçersiz seçim. Lütfen geçerli bir numara girin.")