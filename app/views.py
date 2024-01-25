from urllib import request
from django.http import JsonResponse
from django.shortcuts import render, redirect
import sounddevice as sd
import soundfile as sf
import sqlite3
import pandas as pd

from .models import heartAudio, lungAudio, heartSound
from .forms import heartAudioForms, lungAudioForm, heartSoundForm
from .DashApp import ecg_dash, rsp_dash, hbr_dash, comp_dash

hr_show, rr_show = 60, 15
current_audio_stream = False
con = sqlite3.connect("../db.sqlite3")
cur = con.cursor()
df_heart = pd.read_sql_query("SELECT * FROM app_heartaudio", con)

# Create your views here.
def index(request):
    global hr_show
    global rr_show
    global current_audio_stream
    global df_heart

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

        audio_path1 = 'app/static/audio/heart/normal_heart/M/combined_audio.wav'
        audio_path2 = 'app/static/audio/heart/normal_heart/A/combined_audio.wav'
        audio_path3 = 'app/static/audio/heart/normal_heart/P/combined_audio.wav'
        audio_path4 = 'app/static/audio/heart/normal_heart/T/combined_audio.wav'
        audio_path5 = 'app/static/audio/heart/normal_heart/E/combined_audio.wav'
        
        if current_audio_stream:
            sd.stop()
            current_audio_stream = False
        
        if 'normal_heart_sound_mitral_valve' in request.POST:
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'M'), 'audio_file_path'].values[0], dtype='float32')
            sd.play(data, fs, device=8, loop = True)
            current_audio_stream = True
        elif 'normal_heart_sound_aortic_valve' in request.POST:
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'A'), 'audio_file_path'].values[0], dtype='float32')
            sd.play(data, fs, device=8, loop = True)
            current_audio_stream = True
        elif 'normal_heart_sound_pulmonary_valve' in request.POST:
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0], dtype='float32')
            sd.play(data, fs, device=8, loop = True)
            current_audio_stream = True
        elif 'normal_heart_sound_tricuspid_valve' in request.POST:
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0], dtype='float32')
            sd.play(data, fs, device=8, loop = True)
            current_audio_stream = True
        elif 'normal_heart_sound_erb_point' in request.POST:
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0], dtype='float32')
            sd.play(data, fs, device=8, loop = True)
            current_audio_stream = True
        else:
            pass

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