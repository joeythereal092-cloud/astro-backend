import os
import time
import io
from datetime import datetime
import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr
from gtts import gTTS
import pygame
from g4f.client import Client

ai_client = Client()

def sprechen(text):
    print(f"\n[JARVIS SPRICHT]: {text}")
    try:
        tts = gTTS(text=text, lang='de', slow=False)
        tts.save("stimme.mp3")
        pygame.mixer.music.load("stimme.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.unload()
        if os.path.exists("stimme.mp3"):
            os.remove("stimme.mp3")
    except Exception as e:
        print(f"[AUDIO FEHLER]: {e}")

def frage_ki(frage):
    try:
        prompt = f"Antworte in maximal 2 kurzen Sätzen auf Deutsch, leicht verständlich: {frage}"
        response = ai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[KI FEHLER]: {e}")
        return "Entschuldigung, dazu konnte ich gerade keine Antwort finden."

def verarbeite_befehl(satz):
    if "uhr" in satz or "spät" in satz:
        jetzt = datetime.now().strftime("%H:%M")
        return f"Es ist jetzt {jetzt} Uhr."
    elif "datum" in satz or "tag" in satz:
        heute = datetime.now().strftime("%d.%m.%Y")
        return f"Heute ist der {heute}."
    else:
        return frage_ki(satz)

def ton_aufnehmen(sekunden=5):
    samplerate = 16000
    aufnahme = sd.rec(int(sekunden * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    
    wav_io = io.BytesIO()
    wav.write(wav_io, samplerate, aufnahme)
    wav_io.seek(0)
    
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_io) as source:
        audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio, language="de-DE").lower()
        except Exception:
            return ""

def main():
    pygame.mixer.init()
    TRIGGER_WOERTER = ["jarvis", "charvis", "yarvis", "service", "java"]
    print("[SYSTEM] Jarvis läuft lokal auf deinem PC. Drücke Strg+C zum Beenden.")
    
    while True:
        gehoert = ton_aufnehmen(sekunden=5)
        if any(wort in gehoert for wort in TRIGGER_WOERTER):
            print(f"\n[PC GEHÖRT]: '{gehoert}'")
            antwort = verarbeite_befehl(gehoert)
            sprechen(antwort)

if __name__ == '__main__':
    main()