from urllib import request
from django.http import JsonResponse
from django.shortcuts import render, redirect
import time
import sounddevice as sd
import soundfile as sf

from .models import heartAudio, lungAudio, heartSound
from .forms import heartAudioForms, lungAudioForm, heartSoundForm
from .DashApp import ecg_dash, rsp_dash, hbr_dash, comp_dash

hr_show = 60
rr_show = 15

def NormalHeartSound(type, bpm=60):
    audio = "app/static/audio/heart/normal_heart/{}/combined_audio.wav".format(type)
    data, fs = sf.read(audio, dtype='float32')
    delay=60/bpm
    while True:
        sd.play(data, fs, device=8)   #speakers
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

        if 'normal_heart_sound_mitral_valve' in request.POST:
            NormalHeartSound('M')

        context = {
            'hr_show': hr_show,
            'rr_show': rr_show
        }
    else:
        print('Heart Rate is: {}, Breadth Rate is: {}'.format(hr_show, rr_show))
        context = {
            'hr_show': hr_show,
            'rr_show': rr_show
        }
    return render(request, 'index.html', context)