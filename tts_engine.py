import os
import requests
from google.cloud import texttospeech

def generate_google_tts(text, voice_name="en-US-Wavenet-D", output_path="output.mp3"):
    client = texttospeech.TextToSpeechClient()
    
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code=voice_name.split("-")[0] + "-" + voice_name.split("-")[1],
        name=voice_name
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open(output_path, "wb") as out:
        out.write(response.audio_content)

    print("✅ Google TTS ile ses üretildi:", output_path)
    return output_path


def generate_elevenlabs_tts(text, voice_id, api_key, output_path="output.mp3"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8
        }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print("✅ ElevenLabs TTS ile ses üretildi:", output_path)
        return output_path
    else:
        raise Exception(f"❌ ElevenLabs Hatası: {response.text}")
