from urllib import request
from django.http import JsonResponse
from django.shortcuts import render, redirect
import time
import sounddevice as sd
import soundfile as sf
from threading import Thread

from .models import heartAudio, lungAudio
from .forms import heartAudioForms, lungAudioForm, heartNavBarForm
from .DashApp import ecg_dash, rsp_dash, hbr_dash, comp_dash

hr_show = 60
rr_show = 15

def NormalHeartSound():
    audio1 = "app/static/audio/heart/normal_heart/A/combined_audio.wav"
    data1, fs1 = sf.read(audio1, dtype='float32')
    bpm = 60
    delay=60/bpm
    while True:
        sd.play(data1, fs1, device=8)   #speakers
        time.sleep(delay)

# Create your views here.
def index(request):
    global hr_show
    global rr_show
    if request.method == 'POST':
        if 'hr_plus' in request.POST:
            hr_show += 1
            print('\nHeart Rate updated to: {}'.format(hr_show))
        elif 'hr_minus' in request.POST:
            hr_show -= 1
            print('\nHeart Rate updated to: {}'.format(hr_show))
        elif 'rr_plus' in request.POST:
            rr_show += 1
            print('\nBreath Rate updated to: {}'.format(rr_show))
        elif 'rr_minus' in request.POST:
            rr_show -= 1
            print('\nBreath Rate updated to: {}'.format(rr_show))
        else:
            hr_show += 0
            rr_show += 0

        if 'normal_heart_sound' in request.POST:
            Thread(target = NormalHeartSound).start()
        context = {
            'hr_show': hr_show,
            'rr_show': rr_show
        }
    else:
        if 'normal_heart_sound' in request.POST:
            Thread(target = NormalHeartSound).start()

        print('Heart Rate is: {}, Breadth Rate is: {}'.format(hr_show, rr_show))
        context = {
            'hr_show': hr_show,
            'rr_show': rr_show
        }
    return render(request, 'index.html', context)