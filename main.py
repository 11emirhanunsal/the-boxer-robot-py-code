###########################
# IMPORTS
###########################
import os
import queue
import sounddevice as sd
import vosk
import json
import pyttsx3
import pygame
import sys
import threading

###########################
# GLOBAL DEĞİŞKENLER & KONFİGÜRASYON
###########################
# Çıkış için global event
exit_event = threading.Event()

# PYTTsx3 motorunu başlat
engine = pyttsx3.init()

# Kullanıcıdan geçerli bir dil seçmesini iste
while True:
    language = input("Pick your language (tr or eng-us): ").strip().lower()
    if language in ["tr", "eng-us"]:
        break
    print("Invalid choice. Please enter 'tr' or 'eng-us'.")

# Varsayılan değişkenler
Listening, text_1, You_said, hello, bye = "", "", "", "", ""

if language == "eng-us":
    MODEL_PATH = "vosk/eng-us/vosk-model-small-en-us-0.15"
    Listening = "Listening..."
    text_1 = "Text:"
    You_said = "You said:"
    hello = "hello"
    bye = "bye"
    default_response = "I did not understand."
elif language == "tr":
    MODEL_PATH = "vosk/tr/vosk-model-small-tr-0.3"
    Listening = "Dinleniyor..."
    text_1 = "Yazı:"
    You_said = "Anlaşılan:"
    hello = "merhaba"
    bye = "güle güle"
    default_response = "Anlamadım."

# Vosk modelinin varlığını kontrol et
if not os.path.exists(MODEL_PATH):
    print("Lütfen Vosk modelini indir ve klasöre ekle: https://alphacephei.com/vosk/models")
    sys.exit(1)

###########################
# VOSK MODEL & SES TANIMA AYARLARI
###########################
model = vosk.Model(MODEL_PATH)
recognizer = vosk.KaldiRecognizer(model, 16000)

# Ses kuyruğu oluştur
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    q.put(bytes(indata))

###########################
# SES TANIMA FONKSİYONLARI
###########################
def listen():
    """
    Mikrofonu dinler ve ses verisini işleyerek metne çevirir.
    """
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print(Listening)
        while not exit_event.is_set():
            try:
                data = q.get(timeout=0.1)  # exit_event kontrolü için timeout ekledik
            except queue.Empty:
                continue
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower()  # Eşleşmeyi kolaylaştırmak için küçük harf
                if text:
                    print(You_said, text)
                    respond(text)

def respond(text):
    """
    Gelen metne göre yanıt verir; 'hello/merhaba' veya 'bye/güle güle' komutlarını işler.
    """
    if hello in text:
        response = hello
    elif bye in text:
        response = bye
        print("Assistant:", response)
        engine.say(response)
        engine.runAndWait()
        exit_event.set()  # Çıkış sinyalini gönder
        return
    else:
        response = default_response

    print("Assistant:", response)
    engine.say(response)
    engine.runAndWait()

###########################
# PYGAME İNİŞALİZASYON & ARAYÜZ
###########################
pygame.init()
WIDTH, HEIGHT = 1424, 801
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Voice Assistant with Background")

# Arka plan fotoğrafını yükle
try:
    background_image = pygame.image.load("img/arka_plan.png").convert()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
except Exception as e:
    print("Background image could not be loaded:", e)
    background_image = None

# Ayarlar butonunu yükle ve boyutlandır (64x64) - Sağ üst köşe
try:
    settings_button_image = pygame.image.load("img/ayarlar.png").convert_alpha()
    settings_button_image = pygame.transform.scale(settings_button_image, (64, 64))
except Exception as e:
    print("Settings button image could not be loaded:", e)
    settings_button_image = None
settings_button_rect = pygame.Rect(WIDTH - 64 - 10, 10, 64, 64)

# Bilgi butonunu yükle ve boyutlandır (64x64) - Sol üst köşe
try:
    info_button_image = pygame.image.load("img/bilgi.png").convert_alpha()
    info_button_image = pygame.transform.scale(info_button_image, (64, 64))
except Exception as e:
    print("Info button image could not be loaded:", e)
    info_button_image = None
info_button_rect = pygame.Rect(10, 10, 64, 64)

###########################
# SES TANIMA İÇİN THREAD BAŞLATMA
###########################
listen_thread = threading.Thread(target=listen, daemon=True)
listen_thread.start()

###########################
# ANA PYGAME DÖNGÜSÜ (ETKİNLİK & ÇİZİM)
###########################
clock = pygame.time.Clock()
running = True

while running and not exit_event.is_set():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            exit_event.set()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Ayarlar butonuna tıklanıp tıklanmadığını kontrol et
            if settings_button_rect.collidepoint(event.pos):
                print("Ayarlar butonuna tıklandı!")
                # Buraya ayarlar ekranını açma kodları ekleyebilirsiniz.
            # Bilgi butonuna tıklanıp tıklanmadığını kontrol et
            elif info_button_rect.collidepoint(event.pos):
                print("Bilgi butonuna tıklandı!")
                # Buraya bilgi ekranını açma kodları ekleyebilirsiniz.

    # Arka planı çiz
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill((50, 50, 50))

    # Ayarlar butonunu çiz
    if settings_button_image:
        screen.blit(settings_button_image, settings_button_rect)
    else:
        pygame.draw.rect(screen, (100, 100, 100), settings_button_rect)

    # Bilgi butonunu çiz
    if info_button_image:
        screen.blit(info_button_image, info_button_rect)
    else:
        pygame.draw.rect(screen, (100, 100, 100), info_button_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
