from urllib import request
from django.http import JsonResponse
from django.shortcuts import render, redirect
import sounddevice as sd
import soundcard as sc
import soundfile as sf
import sqlite3
import pandas as pd
import threading

from .models import heartAudio, lungAudio, heartSound
from .forms import heartAudioForms, lungAudioForm, heartSoundForm
from .DashApp import ecg_dash, rsp_dash, hbr_dash, comp_dash

hr_show, rr_show = 60, 15
current_audio_stream = False

speakers = sc.all_speakers()
playing_thread = None  # Global variable to keep track of the currently playing thread

def play(index, samples, samplerate, stop_flag):
    global speakers
    while not stop_flag.is_set():
        speaker = speakers[index]
        speaker.play(samples, samplerate)

# Create your views here.
def index(request):
    global hr_show
    global rr_show
    global current_audio_stream
    global playing_thread

    try:
        con = sqlite3.connect("/home/pi/Downloads/Auscultation-Simulator-Application/app/sounds.sqlite3")
    except:
        con = sqlite3.connect("/Users/kumarlaxmikant/Desktop/Visual_Studio/Auscultation-Simulator-Application/app/sounds.sqlite3")
    df_heart = pd.read_sql_query("SELECT * FROM app_heartaudio", con)

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
        
        if current_audio_stream:
            if playing_thread and playing_thread.is_alive():
                playing_thread.join()  # Stop the currently playing audio
            current_audio_stream = False

        stop_flag = threading.Event()
        
        if 'normal_heart_sound_mitral_valve' in request.POST:
            print('Sound Played: Normal Heart, Location: Mitral Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'M'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(1, data, fs, stop_flag))
            playing_thread.start()
            current_audio_stream = True
        elif 'normal_heart_sound_aortic_valve' in request.POST:
            print('Sound Played: Normal Heart, Location: Aortic Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'A'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(1, data, fs, stop_flag))
            playing_thread.start()
            current_audio_stream = True
        elif 'normal_heart_sound_pulmonary_valve' in request.POST:
            print('Sound Played: Normal Heart, Location: Pulmonary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(1, data, fs, stop_flag))
            playing_thread.start()
            current_audio_stream = True
        elif 'normal_heart_sound_tricuspid_valve' in request.POST:
            print('Sound Played: Normal Heart, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(1, data, fs, stop_flag))
            playing_thread.start()
            current_audio_stream = True
        elif 'normal_heart_sound_erb_point' in request.POST:
            print('Sound Played: Normal Heart, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(1, data, fs, stop_flag))
            playing_thread.start()
            current_audio_stream = True
        elif 'split_first_heart_sound_mitral_valve' in request.POST:
            print('Sound Played: Split First Heart, Location: Mitral Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_first_heart_sound') & (df_heart['sound_type'] == 'M'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(2, data, fs, stop_flag))
            playing_thread.start()
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