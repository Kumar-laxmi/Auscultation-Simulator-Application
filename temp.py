import sounddevice as sd
import soundfile as sf
import threading
from threading import Thread
import time

def audioFunc1():
    audio1 = "app/static/audio/heart/normal_heart/A/4.wav"
    data1, fs1 = sf.read(audio1, dtype='float32')
    bpm = 60
    delay=60/bpm
    while True:
        sd.play(data1, fs1, device=1)   #speakers
        time.sleep(delay)

def audioFunc2():
    audio2 = "app/static/audio/heart/opening_snap/A/2.wav"
    data2, fs2 = sf.read(audio2, dtype='float32')
    bpm = 60
    delay=60/bpm
    while True:
        sd.play(data2, fs2, device=3)  #headset
        time.sleep(delay)

if __name__ == '__main__':
    Thread(target = audioFunc1).start()
    Thread(target = audioFunc2).start()