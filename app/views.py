from urllib import request
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import sounddevice as sd
import soundcard as sc
import soundfile as sf
import sqlite3
import pandas as pd
import threading

from .models import heartAudio, lungAudio
from .forms import heartAudioForms, lungAudioForm
from .DashApp import ecg_dash, rsp_dash, hbr_dash, comp_dash

hr_show, rr_show = 60, 15
current_audio_stream = False

try:
    con = sqlite3.connect("/home/pi/Downloads/Auscultation-Simulator-Application/db.sqlite3", check_same_thread=False)
except:
    con = sqlite3.connect("/Users/kumarlaxmikant/Desktop/Visual_Studio/Auscultation-Simulator-Application/db.sqlite3", check_same_thread=False)
cursor = con.cursor()

speakers = sc.all_speakers()
playing_thread = None  # Global variable to keep track of the currently playing thread
stop_flag = threading.Event()

def play(index, samples, samplerate):
    global speakers
    global stop_flag
    while not stop_flag.is_set():
        speaker = speakers[index]
        speaker.play(samples, samplerate)

def heartUpdate(request):
    global hr_show
    global con
    global cursor

    if request.method == 'POST':
        cursor = con.cursor()
        if 'hr_plus' in request.POST:
            hr_show += 1
            cursor.execute("""UPDATE heartrate SET heartrate = heartrate + 1 WHERE default_col=1""")
            con.commit()
            print('\nHeart Rate updated to: {}'.format(hr_show))
        elif 'hr_minus' in request.POST:
            hr_show -= 1
            cursor.execute("""UPDATE heartrate SET heartrate = heartrate - 1 WHERE default_col=1""")
            con.commit()
            print('\nHeart Rate updated to: {}'.format(hr_show))
        else:
            hr_show += 0
        cursor.close()
        return JsonResponse({'message': 'Success!', 'hr_show': hr_show})
    else:
        return HttpResponse("Request method is not a POST")

def breathUpdate(request):
    global rr_show
    global con
    global cursor

    if request.method == 'POST':
        cursor = con.cursor()
        if 'rr_plus' in request.POST:
            rr_show += 1
            cursor.execute("""UPDATE breathrate SET breathrate = breathrate + 1 WHERE default_col=1""")
            con.commit()
            print('\nBreath Rate updated to: {}'.format(rr_show))
        elif 'rr_minus' in request.POST:
            rr_show -= 1
            cursor.execute("""UPDATE breathrate SET breathrate = breathrate - 1 WHERE default_col=1""")
            con.commit()
            print('\nBreath Rate updated to: {}'.format(rr_show))
        else:
            rr_show += 0
        cursor.close()
        return JsonResponse({'message': 'Success!', 'rr_show': rr_show})
    else:
        return HttpResponse("Request method is not a POST")

# Create your views here.
def index(request):
    global hr_show
    global rr_show
    global current_audio_stream
    global playing_thread
    global stop_flag

    try:
        con = sqlite3.connect("/home/pi/Downloads/Auscultation-Simulator-Application/app/sounds.sqlite3", check_same_thread=False)
    except:
        con = sqlite3.connect("/Users/kumarlaxmikant/Desktop/Visual_Studio/Auscultation-Simulator-Application/app/sounds.sqlite3", check_same_thread=False)
    df_heart = pd.read_sql_query("SELECT * FROM app_heartaudio", con)

    if request.method == 'POST':
        if current_audio_stream:
            if playing_thread and playing_thread.is_alive():
                stop_flag.set()
                playing_thread.join()  # Stop the currently playing audio
            current_audio_stream = False
        
        stop_flag = threading.Event()
        
        if 'normal_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Normal Heart, Location: Mitral Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'M'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(1, data, fs))
            playing_thread.start()
            current_audio_stream = True
        elif 'normal_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Normal Heart, Location: Aortic Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'A'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(1, data, fs))
            playing_thread.start()
            current_audio_stream = True
        elif 'normal_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Normal Heart, Location: Pulmonary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(1, data, fs))
            playing_thread.start()
            current_audio_stream = True
        elif 'normal_heart_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Normal Heart, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(1, data, fs))
            playing_thread.start()
            current_audio_stream = True
        elif 'normal_heart_sound_erb_point' in request.POST:
            print('\nSound Played: Normal Heart, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(1, data, fs))
            playing_thread.start()
            current_audio_stream = True
        elif 'split_first_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Split First Heart, Location: Mitral Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_first_heart_sound') & (df_heart['sound_type'] == 'M'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(2, data, fs))
            playing_thread.start()
            current_audio_stream = True
        elif 'split_first_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Split First Heart, Location: Aortic Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_first_heart_sound') & (df_heart['sound_type'] == 'A'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(2, data, fs))
            playing_thread.start()
            current_audio_stream = True
        elif 'split_first_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Split First Heart, Location: Pulmonary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_first_heart_sound') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(2, data, fs))
            playing_thread.start()
            current_audio_stream = True
        elif 'split_first_heart_sound_tricuspid_valvee' in request.POST:
            print('\nSound Played: Split First Heart, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_first_heart_sound') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(2, data, fs))
            playing_thread.start()
            current_audio_stream = True
        elif 'split_first_heart_sound_erb_point' in request.POST:
            print('\nSound Played: Split First Heart, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_first_heart_sound') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(2, data, fs))
            playing_thread.start()
            current_audio_stream = True
        elif 'split_second_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Mitral Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_second_heart_sound') & (df_heart['sound_type'] == 'M'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(3, data, fs))
            playing_thread.start()
            current_audio_stream = True
        elif 'split_second_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Aortic Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_second_heart_sound') & (df_heart['sound_type'] == 'A'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(3, data, fs))
            playing_thread.start()
            current_audio_stream = True
        elif 'split_second_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_second_heart_sound') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(3, data, fs))
            playing_thread.start()
            current_audio_stream = True
        elif 'split_second_heart_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_second_heart_sound') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(3, data, fs))
            playing_thread.start()
            current_audio_stream = True
        elif 'split_second_heart_sound_erb_point' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_second_heart_sound') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread = threading.Thread(target=play, args=(3, data, fs))
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
        cursor.execute("""UPDATE heartrate SET heartrate = '60'""")
        con.commit()
        cursor.execute("""UPDATE breathrate SET breathrate = '15'""")
        con.commit()
        context = {
            'hr_show': hr_show,
            'rr_show': rr_show
        }
    return render(request, 'index.html', context)