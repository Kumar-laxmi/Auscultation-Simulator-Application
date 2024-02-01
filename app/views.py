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

try:
    con = sqlite3.connect("/home/pi/Downloads/Auscultation-Simulator-Application/db.sqlite3", check_same_thread=False)
except:
    con = sqlite3.connect("/Users/kumarlaxmikant/Desktop/Visual_Studio/Auscultation-Simulator-Application/db.sqlite3", check_same_thread=False)
cursor = con.cursor()

speakers = sc.all_speakers()

current_audio_stream_mitral = False
current_audio_stream_aortic = False
current_audio_stream_pulmonary = False
current_audio_stream_tricuspid = False
current_audio_stream_erb = False

playing_thread_mitral = None
playing_thread_aortic = None
playing_thread_pulmonary = None
playing_thread_tricuspid = None
playing_thread_erb = None

stop_flag_mitral = threading.Event()
stop_flag_aortic = threading.Event()
stop_flag_pulmonary = threading.Event()
stop_flag_tricuspid = threading.Event()
stop_flag_erb = threading.Event()

def play_mitral(index, samples, samplerate):
    global speakers
    global stop_flag_mitral
    while not stop_flag_mitral.is_set():
        print('M', end="")
        speaker = speakers[index]
        speaker.play(samples, samplerate)

def play_aortic(index, samples, samplerate):
    global speakers
    global stop_flag_aortic
    while not stop_flag_aortic.is_set():
        print('A', end="")
        speaker = speakers[index]
        speaker.play(samples, samplerate)

def play_pulmonary(index, samples, samplerate):
    global speakers
    global stop_flag_pulmonary
    while not stop_flag_pulmonary.is_set():
        print('P', end="")
        speaker = speakers[index]
        speaker.play(samples, samplerate)

def play_tricuspid(index, samples, samplerate):
    global speakers
    global stop_flag_tricuspid
    while not stop_flag_tricuspid.is_set():
        print('T', end="")
        speaker = speakers[index]
        speaker.play(samples, samplerate)

def play_erb(index, samples, samplerate):
    global speakers
    global stop_flag_erb
    while not stop_flag_erb.is_set():
        print('E', end="")
        speaker = speakers[index]
        speaker.play(samples, samplerate)
        
def heartUpdate(request):
    global hr_show
    global con, cursor

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
    global con, cursor

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
    global hr_show, rr_show

    global current_audio_stream_mitral, current_audio_stream_aortic, current_audio_stream_pulmonary, current_audio_stream_tricuspid, current_audio_stream_erb
    global playing_thread_mitral, playing_thread_aortic, playing_thread_pulmonary, playing_thread_tricuspid, playing_thread_erb
    global stop_flag_mitral, stop_flag_aortic, stop_flag_pulmonary, stop_flag_tricuspid, stop_flag_erb

    try:
        con = sqlite3.connect("/home/pi/Downloads/Auscultation-Simulator-Application/app/sounds.sqlite3", check_same_thread=False)
    except:
        con = sqlite3.connect("/Users/kumarlaxmikant/Desktop/Visual_Studio/Auscultation-Simulator-Application/app/sounds.sqlite3", check_same_thread=False)
    df_heart = pd.read_sql_query("SELECT * FROM app_heartaudio", con)

    if request.method == 'POST':        
        if current_audio_stream_mitral:
            if playing_thread_mitral and playing_thread_mitral.is_alive():
                stop_flag_mitral.set()
                playing_thread_mitral.join()
                print('Destroyed Mitral thread')
                current_audio_stream_mitral = False
                stop_flag_mitral = threading.Event()
        
        if current_audio_stream_aortic:
            if playing_thread_aortic and playing_thread_aortic.is_alive():
                stop_flag_aortic.set()
                playing_thread_aortic.join()
                print('Destroyed Aortic thread')
                current_audio_stream_aortic = False
                stop_flag_aortic = threading.Event()
        
        if current_audio_stream_pulmonary:
            if playing_thread_pulmonary and playing_thread_pulmonary.is_alive():
                stop_flag_pulmonary.set()
                playing_thread_pulmonary.join()
                print('Destroyed Pulmonary thread')
                current_audio_stream_pulmonary = False
                stop_flag_pulmonary = threading.Event()
        
        if current_audio_stream_tricuspid:
            if playing_thread_tricuspid and playing_thread_tricuspid.is_alive():
                stop_flag_tricuspid.set()
                playing_thread_tricuspid.join()
                print('Destroyed Tricuspid thread')
                current_audio_stream_tricuspid = False
                stop_flag_tricuspid = threading.Event()
        
        if current_audio_stream_erb:
            if playing_thread_erb and playing_thread_erb.is_alive():
                stop_flag_erb.set()
                playing_thread_erb.join()
                print('Destroyed Erb thread')
                current_audio_stream_erb = False
                stop_flag_erb = threading.Event()

        # Buttons for Mitral Valve
        if 'normal_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Normal Heart, Location: Mitral Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'M'), 'audio_file_path'].values[0])
            playing_thread_mitral = threading.Thread(target=play_mitral, args=(1, data, fs))
            playing_thread_mitral.start()
            current_audio_stream_mitral = True
        elif 'split_first_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Split First Heart, Location: Mitral Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_first_heart_sound') & (df_heart['sound_type'] == 'M'), 'audio_file_path'].values[0])
            playing_thread_mitral = threading.Thread(target=play_mitral, args=(1, data, fs))
            playing_thread_mitral.start()
            current_audio_stream_mitral = True
        elif 'split_second_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Mitral Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_second_heart_sound') & (df_heart['sound_type'] == 'M'), 'audio_file_path'].values[0])
            playing_thread_mitral = threading.Thread(target=play_mitral, args=(1, data, fs))
            playing_thread_mitral.start()
            current_audio_stream_mitral = True
        elif 'third_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Third Heart (gallop), Location: Mitral Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'third_heart_sound_gallop') & (df_heart['sound_type'] == 'M'), 'audio_file_path'].values[0])
            playing_thread_mitral = threading.Thread(target=play_mitral, args=(1, data, fs))
            playing_thread_mitral.start()
            current_audio_stream_mitral = True
        elif 'fourth_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Fourth Heart (gallop), Location: Mitral Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'fourth_heart_sound_gallop') & (df_heart['sound_type'] == 'M'), 'audio_file_path'].values[0])
            playing_thread_mitral = threading.Thread(target=play_mitral, args=(1, data, fs))
            playing_thread_mitral.start()
            current_audio_stream_mitral = True

        # Buttons for Aortic Valve
        if 'normal_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Normal Heart, Location: Aortic Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'A'), 'audio_file_path'].values[0])
            playing_thread_aortic = threading.Thread(target=play_aortic, args=(2, data, fs))
            playing_thread_aortic.start()
            current_audio_stream_aortic = True
        elif 'split_first_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Split First Heart, Location: Aortic Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_first_heart_sound') & (df_heart['sound_type'] == 'A'), 'audio_file_path'].values[0])
            playing_thread_aortic = threading.Thread(target=play_aortic, args=(2, data, fs))
            playing_thread_aortic.start()
            current_audio_stream_aortic = True
        elif 'split_second_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Aortic Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_second_heart_sound') & (df_heart['sound_type'] == 'A'), 'audio_file_path'].values[0])
            playing_thread_aortic = threading.Thread(target=play_aortic, args=(2, data, fs))
            playing_thread_aortic.start()
            current_audio_stream_aortic = True
        elif 'third_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Third Heart (gallop), Location: Aortic Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'third_heart_sound_gallop') & (df_heart['sound_type'] == 'A'), 'audio_file_path'].values[0])
            playing_thread_aortic = threading.Thread(target=play_aortic, args=(2, data, fs))
            playing_thread_aortic.start()
            current_audio_stream_aortic = True
        elif 'fourth_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Fourth Heart (gallop), Location: Aortic Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'fourth_heart_sound_gallop') & (df_heart['sound_type'] == 'A'), 'audio_file_path'].values[0])
            playing_thread_aortic = threading.Thread(target=play_aortic, args=(2, data, fs))
            playing_thread_aortic.start()
            current_audio_stream_aortic = True
        
        # Buttons for Pulmonary Valve
        if 'normal_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Normal Heart, Location: Pulmonary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
            current_audio_stream_pulmonary = True
        elif 'split_first_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Split First Heart, Location: Pulmonary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_first_heart_sound') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
            current_audio_stream_pulmonary = True
        elif 'split_second_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_second_heart_sound') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
            current_audio_stream_pulmonary = True
        elif 'third_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Third Heart (gallop), Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'third_heart_sound_gallop') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
            current_audio_stream_pulmonary = True
        elif 'fourth_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Fourth Heart (gallop), Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'fourth_heart_sound_gallop') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
            current_audio_stream_pulmonary = True

        # Buttons for Tricuspid Valve
        if 'normal_heart_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Normal Heart, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
            current_audio_stream_tricuspid = True
        elif 'split_first_heart_sound_tricuspid_valvee' in request.POST:
            print('\nSound Played: Split First Heart, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_first_heart_sound') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
            current_audio_stream_tricuspid = True
        elif 'split_second_heart_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_second_heart_sound') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
            current_audio_stream_tricuspid = True
        elif 'third_heart_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Third Heart (gallop), Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'third_heart_sound_gallop') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
            current_audio_stream_tricuspid = True
        elif 'fourth_heart_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Fourth Heart (gallop), Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'fourth_heart_sound_gallop') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
            current_audio_stream_tricuspid = True
        
        # Buttons for Erb Point Valve
        elif 'normal_heart_sound_erb_point' in request.POST:
            print('\nSound Played: Normal Heart, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
            current_audio_stream_erb = True
        elif 'split_first_heart_sound_erb_point' in request.POST:
            print('\nSound Played: Split First Heart, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_first_heart_sound') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
            current_audio_stream_erb = True
        elif 'split_second_heart_sound_erb_point' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_second_heart_sound') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
            current_audio_stream_erb = True
        elif 'third_heart_sound_erb_point' in request.POST:
            print('\nSound Played: Third Heart (gallop), Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'third_heart_sound_gallop') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
            current_audio_stream_erb = True
        elif 'fourth_heart_sound_erb_point' in request.POST:
            print('\nSound Played: Fourth Heart (gallop), Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'fourth_heart_sound_gallop') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
            current_audio_stream_erb = True

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