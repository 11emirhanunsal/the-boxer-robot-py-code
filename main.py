import os
import queue
import sounddevice as sd
import vosk
import json
import pyttsx3

# PYTTsx3 ile sesi dışarı vermek için motor başlat
engine = pyttsx3.init()

# Vosk İngilizce küçük modeli (40MB)
MODEL_PATH = "vosk/vosk-model-small-en-us-0.15"

if not os.path.exists(MODEL_PATH):
    print("Lütfen Vosk modelini indir ve klasöre ekle: https://alphacephei.com/vosk/models")
    exit(1)

model = vosk.Model(MODEL_PATH)
recognizer = vosk.KaldiRecognizer(model, 16000)

# Ses kuyruğu oluştur
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    q.put(bytes(indata))

# Mikrofonu dinle ve sesi işlemeye başla
def listen():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("Listening...")
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    print("You said:", text)
                    respond(text)

# Yanıt verme fonksiyonu
def respond(text):
    if "hello" in text:
        response = "Hello!"
    elif "right punch" in text:
        response = ""
    elif "left punch" in text:
        response = ""
    elif "right punch" in text:
        response = ""
    elif "left punch" in text:
        response = ""
        engine.say(response)
        engine.runAndWait()
        exit()
    else:
        response = "I did not understand."

    print("Assistant:", response)
    engine.say(response)
    engine.runAndWait()

if __name__ == "__main__":
    listen()
