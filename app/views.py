from urllib import request
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
import soundcard as sc
import soundfile as sf
from pydub import AudioSegment
import sqlite3
import pandas as pd
import io
import threading
import time
import os

from .models import heartAudio, lungAudio
from .forms import heartAudioForms, lungAudioForm
from .DashApp import blank_hbr_dash, ecg_dash, rsp_dash, comp_dash
from .DashApp.Heart import mitral_dash, aortic_dash, pulmonary_dash, tricuspid_dash, erb_dash

# Define the signal
hr_show, rr_show = 60, 15   # Initialize the Heart Rate and Breadth Rate
current_mitral_valve_sound, current_aortic_valve_sound, current_pulmonary_valve_sound, current_tricuspid_valve_sound, current_erb_valve_sound = None, None, None, None, None
current_lungs_sound = None
current_bowel_sound = None

speakers = sc.all_speakers()

try:
    con = sqlite3.connect("/home/pi/Auscultation-Simulator-Application/db.sqlite3", check_same_thread=False)
except:
    con = sqlite3.connect("/Users/kumarlaxmikant/Desktop/Visual_Studio/Auscultation-Simulator-Application/db.sqlite3", check_same_thread=False)
df_heart = pd.read_sql_query("SELECT * FROM app_heartaudio", con)
df_lungs = pd.read_sql_query("SELECT * FROM app_lungaudio", con)
df_bowel = pd.read_sql_query("SELECT * FROM app_bowelaudio", con)

playing_thread_mitral, playing_thread_aortic, playing_thread_pulmonary, playing_thread_tricuspid, playing_thread_erb = None, None, None, None, None
playing_thread_lungs, playing_thread_bowel = None, None

stop_flag_mitral, stop_flag_aortic, stop_flag_pulmonary, stop_flag_tricuspid, stop_flag_erb = threading.Event(), threading.Event(), threading.Event(), threading.Event(), threading.Event()
stop_flag_lungs, stop_flag_bowel = threading.Event(), threading.Event()

def play_mitral(index, samples, samplerate):
    global speakers, stop_flag_mitral, current_mitral_valve_sound, hr_show
    delay_seconds = 60 / hr_show
    while not stop_flag_mitral.is_set():
        speaker = speakers[index]
        speaker.play(samples, samplerate)
        time.sleep(delay_seconds)

def play_aortic(index, samples, samplerate):
    global speakers, stop_flag_aortic, current_aortic_valve_sound, hr_show
    delay_seconds = 60 / hr_show
    while not stop_flag_aortic.is_set():
        speaker = speakers[index]
        speaker.play(samples, samplerate)
        time.sleep(delay_seconds)

def play_pulmonary(index, samples, samplerate):
    global speakers, stop_flag_pulmonary, current_pulmonary_valve_sound, hr_show
    delay_seconds = 60 / hr_show
    while not stop_flag_pulmonary.is_set():
        speaker = speakers[index]
        speaker.play(samples, samplerate)
        time.sleep(delay_seconds)

def play_tricuspid(index, samples, samplerate):
    global speakers, stop_flag_tricuspid, current_tricuspid_valve_sound, hr_show
    delay_seconds = 60 / hr_show
    while not stop_flag_tricuspid.is_set():
        speaker = speakers[index]
        speaker.play(samples, samplerate)
        time.sleep(delay_seconds)

def play_erb(index, samples, samplerate):
    global speakers, stop_flag_erb, current_erb_valve_sound, hr_show
    delay_seconds = 60 / hr_show
    while not stop_flag_erb.is_set():
        speaker = speakers[index]
        speaker.play(samples, samplerate)
        time.sleep(delay_seconds)

def play_lungs(index, samples, samplerate):
    global speakers, stop_flag_lungs, current_lungs_sound, rr_show
    delay_seconds = 60 / rr_show
    while not stop_flag_lungs.is_set():
        speaker = speakers[index]
        speaker.play(samples, samplerate)
        time.sleep(delay_seconds)

def play_bowel(index, samples, samplerate):
    global speakers, stop_flag_bowel, current_bowel_sound, rr_show
    delay_seconds = 60 / rr_show
    while not stop_flag_bowel.is_set():
        speaker = speakers[index]
        speaker.play(samples, samplerate)
        time.sleep(delay_seconds)
        
def heartUpdate(request):
    global hr_show, current_mitral_valve_sound, current_aortic_valve_sound, current_pulmonary_valve_sound, current_tricuspid_valve_sound, current_erb_valve_sound

    if request.method == 'POST':
        if 'hr_plus' in request.POST:
            hr_show += 1
            print('\nHeart Rate updated to: {}'.format(hr_show))
        elif 'hr_minus' in request.POST:
            hr_show -= 1
            print('\nHeart Rate updated to: {}'.format(hr_show))
        else:
            hr_show += 0
        
        if current_mitral_valve_sound is not None:
            start_mitral_thread(current_mitral_valve_sound)
        if current_aortic_valve_sound is not None:
            start_aortic_thread(current_aortic_valve_sound)
        if current_pulmonary_valve_sound is not None:
            start_pulmonary_thread(current_pulmonary_valve_sound)
        if current_tricuspid_valve_sound is not None:
            start_tricuspid_thread(current_tricuspid_valve_sound)
        if current_erb_valve_sound is not None:
            start_erb_thread(current_erb_valve_sound)
        return JsonResponse({'message': 'Success!', 'hr_show': hr_show})
    else:
        return HttpResponse("Request method is not a POST")

def breathUpdate(request):
    global rr_show
    global current_lungs_sound, current_bowel_sound

    if request.method == 'POST':
        if 'rr_plus' in request.POST:
            rr_show += 1
            print('\nBreath Rate updated to: {}'.format(rr_show))
        elif 'rr_minus' in request.POST:
            rr_show -= 1
            print('\nBreath Rate updated to: {}'.format(rr_show))
        else:
            rr_show += 0

        if current_lungs_sound is not None:
            start_lungs_thread(current_lungs_sound)
        if current_bowel_sound is not None:
            start_bowel_thread(current_bowel_sound)
        return JsonResponse({'message': 'Success!', 'rr_show': rr_show})
    else:
        return HttpResponse("Request method is not a POST")

def mitralVolumeChange(request):
    global current_mitral_valve_sound
    if request.method == 'POST':
        if request.POST['identifier'] == current_mitral_valve_sound:
            volume = request.POST['rangeValue']
            os.system('amixer -c 3 set Speaker {}%'.format(volume))
            print('Mitral Valve\'s Volume updated to {}%'.format(volume))
        return JsonResponse({'message': 'Success!'})
    else:
        return HttpResponse("Request method is not a POST")

def aorticVolumeChange(request):
    global current_aortic_valve_sound
    if request.method == 'POST':
        if request.POST['identifier'] == current_aortic_valve_sound:
            volume = request.POST['rangeValue']
            os.system('amixer -c 4 set Speaker {}%'.format(volume))
            print('Aortic Valve\'s Volume updated to {}%'.format(volume))
        return JsonResponse({'message': 'Success!'})
    else:
        return HttpResponse("Request method is not a POST")

def pulmonaryVolumeChange(request):
    global current_pulmonary_valve_sound
    if request.method == 'POST':
        if request.POST['identifier'] == current_pulmonary_valve_sound:
            volume = request.POST['rangeValue']
            os.system('amixer -c 5 set Speaker {}%'.format(volume))
            print('Pulmonary Valve\'s Volume updated to {}%'.format(volume))
        return JsonResponse({'message': 'Success!'})
    else:
        return HttpResponse("Request method is not a POST")

def tricuspidVolumeChange(request):
    global current_tricuspid_valve_sound
    if request.method == 'POST':
        if request.POST['identifier'] == current_tricuspid_valve_sound:
            volume = request.POST['rangeValue']
            os.system('amixer -c 6 set Speaker {}%'.format(volume))
            print('Tricuspid Valve\'s Volume updated to {}%'.format(volume))
        return JsonResponse({'message': 'Success!'})
    else:
        return HttpResponse("Request method is not a POST")

def erbVolumeChange(request):
    global current_erb_valve_sound
    if request.method == 'POST':
        if request.POST['identifier'] == current_erb_valve_sound:
            volume = request.POST['rangeValue']
            os.system('amixer -c 7 set Speaker {}%'.format(volume))
            print('Erb Valve\'s Volume updated to {}%'.format(volume))
        return JsonResponse({'message': 'Success!'})
    else:
        return HttpResponse("Request method is not a POST")

def lungsVolumeChange(request):
    global current_lungs_sound
    if request.method == 'POST':
        if request.POST['identifier'] == current_lungs_sound:
            volume = request.POST['rangeValue']
            os.system('amixer -c 8 set Speaker {}%'.format(volume))
            print('Lungs\'s Volume updates to {}%'.format(volume))
        return JsonResponse({'message': 'Success!'})
    else:
        return HttpResponse("Request method is not a POST")

def bowelVolumeChange(request):
    global current_bowel_sound
    if request.method == 'POST':
        if request.POST['identifier'] == current_bowel_sound:
            volume = request.POST['rangeValue']
            os.system('amixer -c 9 set Speaker {}%'.format(volume))
            print('Bowel\'s Volume updates to {}%'.format(volume))
        return JsonResponse({'message': 'Success!'})
    else:
        return HttpResponse("Request method is not a POST")

def start_mitral_thread(sound_name):
    global playing_thread_mitral, stop_flag_mitral, hr_show, current_mitral_valve_sound
    if playing_thread_mitral and playing_thread_mitral.is_alive():
        stop_flag_mitral.set()  # Set the reload flag to signal the thread to stop
        playing_thread_mitral.join()
        print('Destroyed Mitral thread')
        stop_flag_mitral = threading.Event()

    # Start a new thread
    current_mitral_valve_sound = sound_name
    audio_path = df_heart.loc[(df_heart['sound_name'] == sound_name) & (df_heart['sound_type'] == 'M'), 'audio_file_path'].values[0]
    heartbeat = AudioSegment.from_file(audio_path, format="wav")
    speed_multiplier = hr_show / 60.0  # Assuming 60 BPM as the baseline
    adjusted_heartbeat = heartbeat.speedup(playback_speed=speed_multiplier)
    exported_data = adjusted_heartbeat.export(format="wav").read()
    data, fs = sf.read(io.BytesIO(exported_data))
    playing_thread_mitral = threading.Thread(target=play_mitral, args=(1, data, fs))
    playing_thread_mitral.start()

def start_aortic_thread(sound_name):
    global playing_thread_aortic, stop_flag_aortic, hr_show, current_aortic_valve_sound
    if playing_thread_aortic and playing_thread_aortic.is_alive():
        stop_flag_aortic.set()  # Set the reload flag to signal the thread to stop
        playing_thread_aortic.join()
        print('Destroyed Aortic thread')
        stop_flag_aortic = threading.Event()

    # Start a new thread
    current_aortic_valve_sound = sound_name
    audio_path = df_heart.loc[(df_heart['sound_name'] == sound_name) & (df_heart['sound_type'] == 'A'), 'audio_file_path'].values[0]
    heartbeat = AudioSegment.from_file(audio_path, format="wav")
    speed_multiplier = hr_show / 60.0  # Assuming 60 BPM as the baseline
    adjusted_heartbeat = heartbeat.speedup(playback_speed=speed_multiplier)
    exported_data = adjusted_heartbeat.export(format="wav").read()
    data, fs = sf.read(io.BytesIO(exported_data))
    playing_thread_aortic = threading.Thread(target=play_aortic, args=(2, data, fs))
    playing_thread_aortic.start()

def start_pulmonary_thread(sound_name):
    global playing_thread_pulmonary, stop_flag_pulmonary, hr_show, current_pulmonary_valve_sound
    if playing_thread_pulmonary and playing_thread_pulmonary.is_alive():
        stop_flag_pulmonary.set()  # Set the reload flag to signal the thread to stop
        playing_thread_pulmonary.join()
        print('Destroyed Pulmonary thread')
        stop_flag_pulmonary = threading.Event()

    # Start a new thread
    current_pulmonary_valve_sound = sound_name
    audio_path = df_heart.loc[(df_heart['sound_name'] == sound_name) & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0]
    heartbeat = AudioSegment.from_file(audio_path, format="wav")
    speed_multiplier = hr_show / 60.0  # Assuming 60 BPM as the baseline
    adjusted_heartbeat = heartbeat.speedup(playback_speed=speed_multiplier)
    exported_data = adjusted_heartbeat.export(format="wav").read()
    data, fs = sf.read(io.BytesIO(exported_data))
    playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
    playing_thread_pulmonary.start()

def start_tricuspid_thread(sound_name):
    global playing_thread_tricuspid, stop_flag_tricuspid, hr_show, current_tricuspid_valve_sound
    if playing_thread_tricuspid and playing_thread_tricuspid.is_alive():
        stop_flag_tricuspid.set()  # Set the reload flag to signal the thread to stop
        playing_thread_tricuspid.join()
        print('Destroyed Tricuspid thread')
        stop_flag_tricuspid = threading.Event()

    # Start a new thread
    current_tricuspid_valve_sound = sound_name
    audio_path = df_heart.loc[(df_heart['sound_name'] == sound_name) & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0]
    heartbeat = AudioSegment.from_file(audio_path, format="wav")
    speed_multiplier = hr_show / 60.0  # Assuming 60 BPM as the baseline
    adjusted_heartbeat = heartbeat.speedup(playback_speed=speed_multiplier)
    exported_data = adjusted_heartbeat.export(format="wav").read()
    data, fs = sf.read(io.BytesIO(exported_data))
    playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
    playing_thread_tricuspid.start()

def start_erb_thread(sound_name):
    global playing_thread_erb, stop_flag_erb, hr_show, current_erb_valve_sound
    if playing_thread_erb and playing_thread_erb.is_alive():
        stop_flag_erb.set()  # Set the reload flag to signal the thread to stop
        playing_thread_erb.join()
        print('Destroyed Erb thread')
        stop_flag_erb = threading.Event()

    # Start a new thread
    current_erb_valve_sound = sound_name
    audio_path = df_heart.loc[(df_heart['sound_name'] == sound_name) & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0]
    heartbeat = AudioSegment.from_file(audio_path, format="wav")
    speed_multiplier = hr_show / 60.0  # Assuming 60 BPM as the baseline
    adjusted_heartbeat = heartbeat.speedup(playback_speed=speed_multiplier)
    exported_data = adjusted_heartbeat.export(format="wav").read()
    data, fs = sf.read(io.BytesIO(exported_data))
    playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
    playing_thread_erb.start()

def start_lungs_thread(sound_name):
    global playing_thread_lungs, stop_flag_lungs, rr_show, current_lungs_valve_sound
    if playing_thread_lungs and playing_thread_lungs.is_alive():
        stop_flag_lungs.set()  # Set the reload flag to signal the thread to stop
        playing_thread_lungs.join()
        print('Destroyed Lungs thread')
        stop_flag_lungs = threading.Event()

    # Start a new thread
    current_lungs_valve_sound = sound_name
    audio_path = df_lungs.loc[(df_lungs['sound_name'] == sound_name) & (df_lungs['sound_type'] == 'E'), 'audio_file_path'].values[0]
    lungsbeat = AudioSegment.from_file(audio_path, format="wav")
    speed_multiplier = rr_show / 60.0  # Assuming 60 BPM as the baseline
    adjusted_lungsbeat = lungsbeat.speedup(playback_speed=speed_multiplier)
    exported_data = adjusted_lungsbeat.export(format="wav").read()
    data, fs = sf.read(io.BytesIO(exported_data))
    playing_thread_lungs = threading.Thread(target=play_lungs, args=(6, data, fs))
    playing_thread_lungs.start()

def start_bowel_thread(sound_name):
    global playing_thread_bowel, stop_flag_bowel, rr_show, current_bowel_valve_sound
    if playing_thread_bowel and playing_thread_bowel.is_alive():
        stop_flag_bowel.set()  # Set the reload flag to signal the thread to stop
        playing_thread_bowel.join()
        print('Destroyed Bowel thread')
        stop_flag_bowel = threading.Event()

    # Start a new thread
    current_bowel_valve_sound = sound_name
    audio_path = df_bowel.loc[(df_bowel['sound_name'] == sound_name) & (df_bowel['sound_type'] == 'E'), 'audio_file_path'].values[0]
    bowelbeat = AudioSegment.from_file(audio_path, format="wav")
    speed_multiplier = rr_show / 60.0  # Assuming 60 BPM as the baseline
    adjusted_bowelbeat = bowelbeat.speedup(playback_speed=speed_multiplier)
    exported_data = adjusted_bowelbeat.export(format="wav").read()
    data, fs = sf.read(io.BytesIO(exported_data))
    playing_thread_bowel = threading.Thread(target=play_bowel, args=(7, data, fs))
    playing_thread_bowel.start()

def soundPlay(request):
    if request.method == 'POST':
        # Buttons for Mitral Valve
        if 'normal_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Normal Heart, Location: Mitral Valve')
            start_mitral_thread('normal_heart')
        elif 'split_first_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Split First Heart, Location: Mitral Valve')
            start_mitral_thread('split_first_heart')
        elif 'split_second_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Mitral Valve')
            start_mitral_thread('split_second_heart')
        elif 'third_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Third Heart (gallop), Location: Mitral Valve')
            start_mitral_thread('third_heart')
        elif 'fourth_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Fourth Heart (gallop), Location: Mitral Valve')
            start_mitral_thread('fourth_heart')
        elif 'functional_murmur_sound_mitral_valve' in request.POST:
            print('\nSound Played: Functional Murmur, Location: Mitral Valve')
            start_mitral_thread('functional_murmur')
        elif 'diastolic_murmur_sound_mitral_valve' in request.POST:
            print('\nSound Played: Diastolic Murmur, Location: Mitral Valve')
            start_mitral_thread('diastolic_murmur')
        elif 'opening_snap_sound_mitral_valve' in request.POST:
            print('\nSound Played: Opening Snap, Location: Mitral Valve')
            start_mitral_thread('opening_snap')
        elif 'holosystolic_murmur_sound_mitral_valve' in request.POST:
            print('\nSound Played: Holosystolic Murmur, Location: Mitral Valve')
            start_mitral_thread('holosystolic_murmur')
        elif 'early_systolic_murmur_sound_mitral_valve' in request.POST:
            print('\nSound Played: Early Systolic Murmur, Location: Mitral Valve')
            start_mitral_thread('early_systolic_murmur')
        elif 'mid_systolic_murmur_sound_mitral_valve' in request.POST:
            print('\nSound Played: Mid Systolic Murmur, Location: Mitral Valve')
            start_mitral_thread('mid_systolic_murmur')
        elif 'continuous_murmur_sound_mitral_valve' in request.POST:
            print('\nSound Played: Continuous Murmur, Location: Mitral Valve')
            start_mitral_thread('continuous_murmur')
        elif 'austin_flint_murmur_sound_mitral_valve' in request.POST:
            print('\nSound Played: Austin Flint Murmur, Location: Mitral Valve')
            start_mitral_thread('austin_flint_murmur')
        elif 'pericardial_rub_sound_mitral_valve' in request.POST:
            print('\nSound Played: Pericardial Rub, Location: Mitral Valve')
            start_mitral_thread('pericardial_rub')
        elif 'graham_steell_murmur_sound_mitral_valve' in request.POST:
            print('\nSound Played: Graham Steell Murmur, Location: Mitral Valve')
            start_mitral_thread('pericardial_rub')
        elif 'aortic_valve_regurgitation_sound_mitral_valve' in request.POST:
            print('\nSound Played: Aortic Valve Regurgitation, Location: Mitral Valve')
            start_mitral_thread('aortic_valve_regurgitation')
        elif 'aortic_valve_stenosis_sound_mitral_valve' in request.POST:
            print('\nSound Played: Aortic Valve Stenosis, Location: Mitral Valve')
            start_mitral_thread('aortic_valve_stenosis')
        elif 'aortic_valve_stenosis_regurgitation_sound_mitral_valve' in request.POST:
            print('\nSound Played: Aortic Valve Stenosis Regurgitation, Location: Mitral Valve')
            start_mitral_thread('aortic_stenosis_regurgitation')
        elif 'congenital_aortic_stenosis_sound_mitral_valve' in request.POST:
            print('\nSound Played: Congenital Aortic Stenosis, Location: Mitral Valve')
            start_mitral_thread('congenital_aortic_stenosis')
        elif 'mitral_valve_regurgitation_sound_mitral_valve' in request.POST:
            print('\nSound Played: Mitral Valve Regurgitation, Location: Mitral Valve')
            start_mitral_thread('mitral_valve_regurgitation')
        elif 'mitral_valve_stenosis_sound_mitral_valve' in request.POST:
            print('\nSound Played: Mitral Valve Stenosis, Location: Mitral Valve')
            start_mitral_thread('mitral_valve_stenosis')
        elif 'mitral_valve_prelapse_sound_mitral_valve' in request.POST:
            print('\nSound Played: Mitral Valve Prelapse, Location: Mitral Valve')
            start_mitral_thread('mitral_valve_prelapse')
        elif 'mitral_stenosis_regurgitation_sound_mitral_valve' in request.POST:
            print('\nSound Played: Mitral Stenosis Regurgitation, Location: Mitral Valve')
            start_mitral_thread('mitral_stenosis_regurgitation')
        elif 'mitral_stenosis_tricuspid_regurgitation_sound_mitral_valve' in request.POST:
            print('\nSound Played: Mitral Stenosis Tricuspid Regurgitation, Location: Mitral Valve')
            start_mitral_thread('mitral_stenosis_tricuspid_regurgitation')
        elif 'pulmonary_valve_stenosis_sound_mitral_valve' in request.POST:
            print('\nSound Played: Pulmonary Valve Stenosis, Location: Mitral Valve')
            start_mitral_thread('pulmonary_valve_stenosis')
        elif 'pulmonary_valve_regurgitation_sound_mitral_valve' in request.POST:
            print('\nSound Played: Pulmonary Valve Regurgitation, Location: Mitral Valve')
            start_mitral_thread('pulmonary_valve_regurgitation')
        elif 'tricuspid_valve_regurgitation_sound_mitral_valve' in request.POST:
            print('\nSound Played: Tricuspid Valve Regurgitation, Location: Mitral Valve')
            start_mitral_thread('tricuspid_valve_regurgitation')    
        elif 'coarctation_of_the_aorta_sound_mitral_valve' in request.POST:
            print('\nSound Played: Coarctation of the Aorta, Location: Mitral Valve')
            start_mitral_thread('coarctation_of_the_aorta')
        elif 'hypertrophic_cardiomyopathy_sound_mitral_valve' in request.POST:
            print('\nSound Played: Hypertrophic Cardiomyopathy, Location: Mitral Valve')
            start_mitral_thread('hypertrophic_cardiomyopathy')
        elif 'patent_ductus_arteriosus_sound_mitral_valve' in request.POST:
            print('\nSound Played: Patent Ductus Arteriosus, Location: Mitral Valve')
            start_mitral_thread('patent_ductus_arteriosus')
        elif 'atrial_septal_defect_sound_mitral_valve' in request.POST:
            print('\nSound Played: Atrial Septal Defect, Location: Mitral Valve')
            start_mitral_thread('atrial_septal_defect')
        elif 'ventricular_septal_defect_sound_mitral_valve' in request.POST:
            print('\nSound Played: Ventricular Septal Defect, Location: Mitral Valve')
            start_mitral_thread('ventricular_septal_defect')
        elif 'acute_myocardial_infarction_sound_mitral_valve' in request.POST:
            print('\nSound Played: Acute Myocardial Infaction, Location: Mitral Valve')
            start_mitral_thread('acute_myocardial_infarction')
        elif 'congestive_heart_failure_sound_mitral_valve' in request.POST:
            print('\nSound Played: Congestive Heart Failure, Location: Mitral Valve')
            start_mitral_thread('congestive_heart_failure')
        elif 'systemic_hypertension_sound_mitral_valve' in request.POST:
            print('\nSound Played: Systemic Hypertension, Location: Mitral Valve')
            start_mitral_thread('systemic_hypertension')
        elif 'acute_pericarditis_sound_mitral_valve' in request.POST:
            print('\nSound Played: Acute Pericarditis, Location: Mitral Valve')
            start_mitral_thread('acute_pericarditis')
        elif 'dilated_cardiomyopathy_sound_mitral_valve' in request.POST:
            print('\nSound Played: Dilated Cardiomyopathy, Location: Mitral Valve')
            start_mitral_thread('dilated_cardiomyopathy')
        elif 'pulmonary_hypertension_sound_mitral_valve' in request.POST:
            print('\nSound Played: Pulmonary Hypertension, Location: Mitral Valve')
            start_mitral_thread('pulmonary_hypertension')
        elif 'tetralogy_of_fallot_sound_mitral_valve' in request.POST:
            print('\nSound Played: Tetralogy of Fallot, Location: Mitral Valve')
            start_mitral_thread('tetralogy_of_fallot')
        elif 'ventricular_aneurysm_sound_mitral_valve' in request.POST:
            print('\nSound Played: Ventricular Aneurysm, Location: Mitral Valve')
            start_mitral_thread('ventricular_aneurysm')
        elif 'ebstein_anomaly_sound_mitral_valve' in request.POST:
            print('\nSound Played: Ebstein Anomaly, Location: Mitral Valve')
            start_mitral_thread('ebsteins_anomaly')

        # Buttons for Aortic Valve
        if 'normal_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Normal Heart, Location: Aortic Valve')
            start_aortic_thread('normal_heart')
        elif 'split_first_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Split First Heart, Location: Aortic Valve')
            start_aortic_thread('split_first_heart')
        elif 'split_second_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Aortic Valve')
            start_aortic_thread('split_second_heart')
        elif 'third_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Third Heart (gallop), Location: Aortic Valve')
            start_aortic_thread('third_heart')
        elif 'fourth_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Fourth Heart (gallop), Location: Aortic Valve')
            start_aortic_thread('fourth_heart')
        elif 'functional_murmur_sound_aortic_valve' in request.POST:
            print('\nSound Played: Functional Murmur, Location: Aortic Valve')
            start_aortic_thread('functional_murmur')
        elif 'diastolic_murmur_sound_aortic_valve' in request.POST:
            print('\nSound Played: Diastolic Murmur, Location: Aortic Valve')
            start_aortic_thread('diastolic_murmur')
        elif 'opening_snap_sound_aortic_valve' in request.POST:
            print('\nSound Played: Opening Snap, Location: Aortic Valve')
            start_aortic_thread('opening_snap')
        elif 'holosystolic_murmur_sound_aortic_valve' in request.POST:
            print('\nSound Played: Holosystolic Murmur, Location: Aortic Valve')
            start_aortic_thread('holosystolic_murmur')
        elif 'early_systolic_murmur_sound_aortic_valve' in request.POST:
            print('\nSound Played: Early Systolic Murmur, Location: Aortic Valve')
            start_aortic_thread('early_systolic_murmur')
        elif 'mid_systolic_murmur_sound_aortic_valve' in request.POST:
            print('\nSound Played: Mid Systolic Murmur, Location: Aortic Valve')
            start_aortic_thread('mid_systolic_murmur')
        elif 'continuous_murmur_sound_aortic_valve' in request.POST:
            print('\nSound Played: Continuous Murmur, Location: Aortic Valve')
            start_aortic_thread('continuous_murmur')
        elif 'austin_flint_murmur_sound_aortic_valve' in request.POST:
            print('\nSound Played: Austin Flint Murmur, Location: Aortic Valve')
            start_aortic_thread('austin_flint_murmur')
        elif 'pericardial_rub_sound_aortic_valve' in request.POST:
            print('\nSound Played: Pericardial Rub, Location: Aortic Valve')
            start_aortic_thread('pericardial_rub')
        elif 'graham_steell_murmur_sound_aortic_valve' in request.POST:
            print('\nSound Played: Graham Steell Murmur, Location: Aortic Valve')
            start_aortic_thread('pericardial_rub')
        elif 'aortic_valve_regurgitation_sound_aortic_valve' in request.POST:
            print('\nSound Played: Aortic Valve Regurgitation, Location: Aortic Valve')
            start_aortic_thread('aortic_valve_regurgitation')
        elif 'aortic_valve_stenosis_sound_aortic_valve' in request.POST:
            print('\nSound Played: Aortic Valve Stenosis, Location: Aortic Valve')
            start_aortic_thread('aortic_valve_stenosis')
        elif 'aortic_valve_stenosis_regurgitation_sound_aortic_valve' in request.POST:
            print('\nSound Played: Aortic Valve Stenosis Regurgitation, Location: Aortic Valve')
            start_aortic_thread('aortic_stenosis_regurgitation')
        elif 'congenital_aortic_stenosis_sound_aortic_valve' in request.POST:
            print('\nSound Played: Congenital Aortic Stenosis, Location: Aortic Valve')
            start_aortic_thread('congenital_aortic_stenosis')
        elif 'mitral_valve_regurgitation_sound_aortic_valve' in request.POST:
            print('\nSound Played: Mitral Valve Regurgitation, Location: Aortic Valve')
            start_aortic_thread('mitral_valve_regurgitation')
        elif 'mitral_valve_stenosis_sound_aortic_valve' in request.POST:
            print('\nSound Played: Mitral Valve Stenosis, Location: Aortic Valve')
            start_aortic_thread('mitral_valve_stenosis')
        elif 'mitral_valve_prelapse_sound_aortic_valve' in request.POST:
            print('\nSound Played: Mitral Valve Prelapse, Location: Aortic Valve')
            start_aortic_thread('mitral_valve_prelapse')
        elif 'mitral_stenosis_regurgitation_sound_aortic_valve' in request.POST:
            print('\nSound Played: Mitral Stenosis Regurgitation, Location: Aortic Valve')
            start_aortic_thread('mitral_stenosis_regurgitation')
        elif 'mitral_stenosis_tricuspid_regurgitation_sound_aortic_valve' in request.POST:
            print('\nSound Played: Mitral Stenosis Tricuspid Regurgitation, Location: Aortic Valve')
            start_aortic_thread('mitral_stenosis_tricuspid_regurgitation')
        elif 'pulmonary_valve_stenosis_sound_aortic_valve' in request.POST:
            print('\nSound Played: Pulmonary Valve Stenosis, Location: Aortic Valve')
            start_aortic_thread('pulmonary_valve_stenosis')
        elif 'pulmonary_valve_regurgitation_sound_aortic_valve' in request.POST:
            print('\nSound Played: Pulmonary Valve Regurgitation, Location: Aortic Valve')
            start_aortic_thread('pulmonary_valve_regurgitation')
        elif 'tricuspid_valve_regurgitation_sound_aortic_valve' in request.POST:
            print('\nSound Played: Tricuspid Valve Regurgitation, Location: Aortic Valve')
            start_aortic_thread('tricuspid_valve_regurgitation')
        elif 'coarctation_of_the_aorta_sound_aortic_valve' in request.POST:
            print('\nSound Played: Coarctation of the Aorta, Location: Aortic Valve')
            start_aortic_thread('coarctation_of_the_aorta')
        elif 'hypertrophic_cardiomyopathy_sound_aortic_valve' in request.POST:
            print('\nSound Played: Hypertrophic Cardiomyopathy, Location: Aortic Valve')
            start_aortic_thread('hypertrophic_cardiomyopathy')
        elif 'patent_ductus_arteriosus_sound_aortic_valve' in request.POST:
            print('\nSound Played: Patent Ductus Arteriosus, Location: Aortic Valve')
            start_aortic_thread('patent_ductus_arteriosus')
        elif 'atrial_septal_defect_sound_aortic_valve' in request.POST:
            print('\nSound Played: Atrial Septal Defect, Location: Aortic Valve')
            start_aortic_thread('atrial_septal_defect')
        elif 'ventricular_septal_defect_sound_aortic_valve' in request.POST:
            print('\nSound Played: Ventricular Septal Defect, Location: Aortic Valve')
            start_aortic_thread('ventricular_septal_defect')
        elif 'acute_myocardial_infarction_sound_aortic_valve' in request.POST:
            print('\nSound Played: Acute Myocardial Infaction, Location: Aortic Valve')
            start_aortic_thread('acute_myocardial_infarction')
        elif 'congestive_heart_failure_sound_aortic_valve' in request.POST:
            print('\nSound Played: Congestive Heart Failure, Location: Aortic Valve')
            start_aortic_thread('congestive_heart_failure')
        elif 'systemic_hypertension_sound_aortic_valve' in request.POST:
            print('\nSound Played: Systemic Hypertension, Location: Aortic Valve')
            start_aortic_thread('systemic_hypertension')
        elif 'acute_pericarditis_sound_aortic_valve' in request.POST:
            print('\nSound Played: Acute Pericarditis, Location: Aortic Valve')
            start_aortic_thread('acute_pericarditis')
        elif 'dilated_cardiomyopathy_sound_aortic_valve' in request.POST:
            print('\nSound Played: Dilated Cardiomyopathy, Location: Aortic Valve')
            start_aortic_thread('dilated_cardiomyopathy')
        elif 'pulmonary_hypertension_sound_aortic_valve' in request.POST:
            print('\nSound Played: Pulmonary Hypertension, Location: Aortic Valve')
            start_aortic_thread('pulmonary_hypertension')
        elif 'tetralogy_of_fallot_sound_aortic_valve' in request.POST:
            print('\nSound Played: Tetralogy of Fallot, Location: Aortic Valve')
            start_aortic_thread('tetralogy_of_fallot')
        elif 'ventricular_aneurysm_sound_aortic_valve' in request.POST:
            print('\nSound Played: Ventricular Aneurysm, Location: Aortic Valve')
            start_aortic_thread('ventricular_aneurysm')
        elif 'ebstein_anomaly_sound_aortic_valve' in request.POST:
            print('\nSound Played: Ebstein Anomaly, Location: Aortic Valve')
            start_aortic_thread('ebsteins_anomaly')
        
        # Buttons for Pulmonary Valve
        if 'normal_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Normal Heart, Location: Pulmonary Valve')
            start_pulmonary_thread('normal_heart')
        elif 'split_first_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Split First Heart, Location: Pulmonary Valve')
            start_pulmonary_thread('split_first_heart')
        elif 'split_second_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Pulmonanary Valve')
            start_pulmonary_thread('split_second_heart')
        elif 'third_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Third Heart (gallop), Location: Pulmonanary Valve')
            start_pulmonary_thread('third_heart')
        elif 'fourth_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Fourth Heart (gallop), Location: Pulmonanary Valve')
            start_pulmonary_thread('fourth_heart')
        elif 'functional_murmur_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Functional Murmur, Location: Pulmonanary Valve')
            start_pulmonary_thread('functional_murmur')
        elif 'diastolic_murmur_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Diastolic Murmur, Location: Pulmonanary Valve')
            start_pulmonary_thread('diastolic_murmur')
        elif 'opening_snap_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Opening Snap, Location: Pulmonanary Valve')
            start_pulmonary_thread('opening_snap')
        elif 'holosystolic_murmur_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Holosystolic Murmur, Location: Pulmonanary Valve')
            start_pulmonary_thread('holosystolic_murmur')
        elif 'early_systolic_murmur_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Early Systolic Murmur, Location: Pulmonanary Valve')
            start_pulmonary_thread('early_systolic_murmur')
        elif 'mid_systolic_murmur_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Mid Systolic Murmur, Location: Pulmonanary Valve')
            start_pulmonary_thread('mid_systolic_murmur')
        elif 'continuous_murmur_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Continuous Murmur, Location: Pulmonanary Valve')
            start_pulmonary_thread('continuous_murmur')
        elif 'austin_flint_murmur_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Austin Flint Murmur, Location: Pulmonanary Valve')
            start_pulmonary_thread('austin_flint_murmur')
        elif 'pericardial_rub_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Pericardial Rub, Location: Pulmonanary Valve')
            start_pulmonary_thread('pericardial_rub')
        elif 'graham_steell_murmur_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Graham Steell Murmur, Location: Pulmonanary Valve')
            start_pulmonary_thread('pericardial_rub')
        elif 'aortic_valve_regurgitation_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Aortic Valve Regurgitation, Location: Pulmonanary Valve')
            start_pulmonary_thread('aortic_valve_regurgitation')
        elif 'aortic_valve_stenosis_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Aortic Valve Stenosis, Location: Pulmonanary Valve')
            start_pulmonary_thread('aortic_valve_stenosis')
        elif 'aortic_valve_stenosis_regurgitation_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Aortic Valve Stenosis Regurgitation, Location: Pulmonanary Valve')
            start_pulmonary_thread('aortic_stenosis_regurgitation')
        elif 'congenital_aortic_stenosis_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Congenital Aortic Stenosis, Location: Pulmonanary Valve')
            start_pulmonary_thread('congenital_aortic_stenosis')
        elif 'mitral_valve_regurgitation_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Mitral Valve Regurgitation, Location: Pulmonanary Valve')
            start_pulmonary_thread('mitral_valve_regurgitation')
        elif 'mitral_valve_stenosis_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Mitral Valve Stenosis, Location: Pulmonanary Valve')
            start_pulmonary_thread('mitral_valve_stenosis')
        elif 'mitral_valve_prelapse_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Mitral Valve Prelapse, Location: Pulmonanary Valve')
            start_pulmonary_thread('mitral_valve_prelapse')
        elif 'mitral_stenosis_regurgitation_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Mitral Stenosis Regurgitation, Location: Pulmonanary Valve')
            start_pulmonary_thread('mitral_stenosis_regurgitation')
        elif 'mitral_stenosis_tricuspid_regurgitation_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Mitral Stenosis Tricuspid Regurgitation, Location: Pulmonanary Valve')
            start_pulmonary_thread('mitral_stenosis_tricuspid_regurgitation')
        elif 'pulmonary_valve_stenosis_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Pulmonary Valve Stenosis, Location: Pulmonanary Valve')
            start_pulmonary_thread('pulmonary_valve_stenosis')
        elif 'pulmonary_valve_regurgitation_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Pulmonary Valve Regurgitation, Location: Pulmonanary Valve')
            start_pulmonary_thread('pulmonary_valve_regurgitation')
        elif 'tricuspid_valve_regurgitation_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Tricuspid Valve Regurgitation, Location: Pulmonanary Valve')
            start_pulmonary_thread('tricuspid_valve_regurgitation')
        elif 'coarctation_of_the_aorta_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Coarctation of the Aorta, Location: Pulmonanary Valve')
            start_pulmonary_thread('coarctation_of_the_aorta')
        elif 'hypertrophic_cardiomyopathy_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Hypertrophic Cardiomyopathy, Location: Pulmonanary Valve')
            start_pulmonary_thread('hypertrophic_cardiomyopathy')
        elif 'patent_ductus_arteriosus_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Patent Ductus Arteriosus, Location: Pulmonanary Valve')
            start_pulmonary_thread('patent_ductus_arteriosus')
        elif 'atrial_septal_defect_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Atrial Septal Defect, Location: Pulmonanary Valve')
            start_pulmonary_thread('atrial_septal_defect')
        elif 'ventricular_septal_defect_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Ventricular Septal Defect, Location: Pulmonanary Valve')
            start_pulmonary_thread('ventricular_septal_defect')
        elif 'acute_myocardial_infarction_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Acute Myocardial Infaction, Location: Pulmonanary Valve')
            start_pulmonary_thread('acute_myocardial_infarction')
        elif 'congestive_heart_failure_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Congestive Heart Failure, Location: Pulmonanary Valve')
            start_pulmonary_thread('congestive_heart_failure')
        elif 'systemic_hypertension_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Systemic Hypertension, Location: Pulmonanary Valve')
            start_pulmonary_thread('systemic_hypertension')
        elif 'acute_pericarditis_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Acute Pericarditis, Location: Pulmonanary Valve')
            start_pulmonary_thread('acute_pericarditis')
        elif 'dilated_cardiomyopathy_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Dilated Cardiomyopathy, Location: Pulmonanary Valve')
            start_pulmonary_thread('dilated_cardiomyopathy')
        elif 'pulmonary_hypertension_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Pulmonary Hypertension, Location: Pulmonanary Valve')
            start_pulmonary_thread('pulmonary_hypertension')
        elif 'tetralogy_of_fallot_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Tetralogy of Fallot, Location: Pulmonanary Valve')
            start_pulmonary_thread('tetralogy_of_fallot')
        elif 'ventricular_aneurysm_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Ventricular Aneurysm, Location: Pulmonanary Valve')
            start_pulmonary_thread('ventricular_aneurysm')
        elif 'ebstein_anomaly_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Ebstein Anomaly, Location: Pulmonanary Valve')
            start_pulmonary_thread('ebsteins_anomaly')

        # Buttons for Tricuspid Valve
        if 'normal_heart_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Normal Heart, Location: Tricuspid Valve')
            start_tricuspid_thread('normal_heart')
        elif 'split_first_heart_sound_tricuspid_valvee' in request.POST:
            print('\nSound Played: Split First Heart, Location: Tricuspid Valve')
            start_tricuspid_thread('split_first_heart')
        elif 'split_second_heart_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Tricuspid Valve')
            start_tricuspid_thread('split_second_heart')
        elif 'third_heart_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Third Heart (gallop), Location: Tricuspid Valve')
            start_tricuspid_thread('third_heart')
        elif 'fourth_heart_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Fourth Heart (gallop), Location: Tricuspid Valve')
            start_tricuspid_thread('fourth_heart')
        elif 'functional_murmur_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Functional Murmur, Location: Tricuspid Valve')
            start_tricuspid_thread('functional_murmur')
        elif 'diastolic_murmur_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Diastolic Murmur, Location: Tricuspid Valve')
            start_tricuspid_thread('diastolic_murmur')
        elif 'opening_snap_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Opening Snap, Location: Tricuspid Valve')
            start_tricuspid_thread('opening_snap')
        elif 'holosystolic_murmur_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Holosystolic Murmur, Location: Tricuspid Valve')
            start_tricuspid_thread('holosystolic_murmur')
        elif 'early_systolic_murmur_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Early Systolic Murmur, Location: Tricuspid Valve')
            start_tricuspid_thread('early_systolic_murmur')
        elif 'mid_systolic_murmur_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Mid Systolic Murmur, Location: Tricuspid Valve')
            start_tricuspid_thread('mid_systolic_murmur')
        elif 'continuous_murmur_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Continuous Murmur, Location: Tricuspid Valve')
            start_tricuspid_thread('continuous_murmur')
        elif 'austin_flint_murmur_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Austin Flint Murmur, Location: Tricuspid Valve')
            start_tricuspid_thread('austin_flint_murmur')
        elif 'pericardial_rub_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Pericardial Rub, Location: Tricuspid Valve')
            start_tricuspid_thread('pericardial_rub')
        elif 'graham_steell_murmur_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Graham Steell Murmur, Location: Tricuspid Valve')
            start_tricuspid_thread('pericardial_rub')
        elif 'aortic_valve_regurgitation_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Aortic Valve Regurgitation, Location: Tricuspid Valve')
            start_tricuspid_thread('aortic_valve_regurgitation')
        elif 'aortic_valve_stenosis_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Aortic Valve Stenosis, Location: Tricuspid Valve')
            start_tricuspid_thread('aortic_valve_stenosis')
        elif 'aortic_valve_stenosis_regurgitation_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Aortic Valve Stenosis Regurgitation, Location: Tricuspid Valve')
            start_tricuspid_thread('aortic_stenosis_regurgitation')
        elif 'congenital_aortic_stenosis_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Congenital Aortic Stenosis, Location: Tricuspid Valve')
            start_tricuspid_thread('congenital_aortic_stenosis')
        elif 'mitral_valve_regurgitation_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Mitral Valve Regurgitation, Location: Tricuspid Valve')
            start_tricuspid_thread('mitral_valve_regurgitation')
        elif 'mitral_valve_stenosis_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Mitral Valve Stenosis, Location: Tricuspid Valve')
            start_tricuspid_thread('mitral_valve_stenosis')
        elif 'mitral_valve_prelapse_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Mitral Valve Prelapse, Location: Tricuspid Valve')
            start_tricuspid_thread('mitral_valve_prelapse')
        elif 'mitral_stenosis_regurgitation_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Mitral Stenosis Regurgitation, Location: Tricuspid Valve')
            start_tricuspid_thread('mitral_stenosis_regurgitation')
        elif 'mitral_stenosis_tricuspid_regurgitation_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Mitral Stenosis Tricuspid Regurgitation, Location: Tricuspid Valve')
            start_tricuspid_thread('mitral_stenosis_tricuspid_regurgitation')
        elif 'pulmonary_valve_stenosis_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Pulmonary Valve Stenosis, Location: Tricuspid Valve')
            start_tricuspid_thread('pulmonary_valve_stenosis')
        elif 'pulmonary_valve_regurgitation_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Pulmonary Valve Regurgitation, Location: Tricuspid Valve')
            start_tricuspid_thread('pulmonary_valve_regurgitation')
        elif 'tricuspid_valve_regurgitation_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Tricuspid Valve Regurgitation, Location: Tricuspid Valve')
            start_tricuspid_thread('tricuspid_valve_regurgitation')
        elif 'coarctation_of_the_aorta_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Coarctation of the Aorta, Location: Tricuspid Valve')
            start_tricuspid_thread('coarctation_of_the_aorta')
        elif 'hypertrophic_cardiomyopathy_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Hypertrophic Cardiomyopathy, Location: Tricuspid Valve')
            start_tricuspid_thread('hypertrophic_cardiomyopathy')
        elif 'patent_ductus_arteriosus_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Patent Ductus Arteriosus, Location: Tricuspid Valve')
            start_tricuspid_thread('patent_ductus_arteriosus')
        elif 'atrial_septal_defect_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Atrial Septal Defect, Location: Tricuspid Valve')
            start_tricuspid_thread('atrial_septal_defect')
        elif 'ventricular_septal_defect_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Ventricular Septal Defect, Location: Tricuspid Valve')
            start_tricuspid_thread('ventricular_septal_defect')
        elif 'acute_myocardial_infarction_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Acute Myocardial Infaction, Location: Tricuspid Valve')
            start_tricuspid_thread('acute_myocardial_infarction')
        elif 'congestive_heart_failure_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Congestive Heart Failure, Location: Tricuspid Valve')
            start_tricuspid_thread('congestive_heart_failure')
        elif 'systemic_hypertension_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Systemic Hypertension, Location: Tricuspid Valve')
            start_tricuspid_thread('systemic_hypertension')
        elif 'acute_pericarditis_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Acute Pericarditis, Location: Tricuspid Valve')
            start_tricuspid_thread('acute_pericarditis')
        elif 'dilated_cardiomyopathy_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Dilated Cardiomyopathy, Location: Tricuspid Valve')
            start_tricuspid_thread('dilated_cardiomyopathy')
        elif 'pulmonary_hypertension_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Pulmonary Hypertension, Location: Tricuspid Valve')
            start_tricuspid_thread('pulmonary_hypertension')
        elif 'tetralogy_of_fallot_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Tetralogy of Fallot, Location: Tricuspid Valve')
            start_tricuspid_thread('tetralogy_of_fallot')
        elif 'ventricular_aneurysm_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Ventricular Aneurysm, Location: Tricuspid Valve')
            start_tricuspid_thread('ventricular_aneurysm')
        elif 'ebstein_anomaly_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Ebstein Anomaly, Location: Tricuspid Valve')
            start_tricuspid_thread('ebsteins_anomaly')
        
        # Buttons for Erb Point Valve
        if 'normal_heart_sound_erb_point' in request.POST:
            print('\nSound Played: Normal Heart, Location: Erb Valve')
            start_erb_thread('normal_heart')
        elif 'split_first_heart_sound_erb_point' in request.POST:
            print('\nSound Played: Split First Heart, Location: Erb Valve')
            start_erb_thread('split_first_heart')
        elif 'split_second_heart_sound_erb_point' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Erb Valve')
            start_erb_thread('split_second_heart')
        elif 'third_heart_sound_erb_point' in request.POST:
            print('\nSound Played: Third Heart (gallop), Location: Erb Valve')
            start_erb_thread('third_heart')
        elif 'fourth_heart_sound_erb_point' in request.POST:
            print('\nSound Played: Fourth Heart (gallop), Location: Erb Valve')
            start_erb_thread('fourth_heart')
        elif 'functional_murmur_sound_erb_point' in request.POST:
            print('\nSound Played: Functional Murmur, Location: Erb Valve')
            start_erb_thread('functional_murmur')
        elif 'diastolic_murmur_sound_erb_point' in request.POST:
            print('\nSound Played: Diastolic Murmur, Location: Erb Valve')
            start_erb_thread('diastolic_murmur')
        elif 'opening_snap_sound_erb_point' in request.POST:
            print('\nSound Played: Opening Snap, Location: Erb Valve')
            start_erb_thread('opening_snap')
        elif 'holosystolic_murmur_sound_erb_point' in request.POST:
            print('\nSound Played: Holosystolic Murmur, Location: Erb Valve')
            start_erb_thread('holosystolic_murmur')
        elif 'early_systolic_murmur_sound_erb_point' in request.POST:
            print('\nSound Played: Early Systolic Murmur, Location: Erb Valve')
            start_erb_thread('early_systolic_murmur')
        elif 'mid_systolic_murmur_sound_erb_point' in request.POST:
            print('\nSound Played: Mid Systolic Murmur, Location: Erb Valve')
            start_erb_thread('mid_systolic_murmur')
        elif 'continuous_murmur_sound_erb_point' in request.POST:
            print('\nSound Played: Continuous Murmur, Location: Erb Valve')
            start_erb_thread('continuous_murmur')
        elif 'austin_flint_murmur_sound_erb_point' in request.POST:
            print('\nSound Played: Austin Flint Murmur, Location: Erb Valve')
            start_erb_thread('austin_flint_murmur')
        elif 'pericardial_rub_sound_erb_point' in request.POST:
            print('\nSound Played: Pericardial Rub, Location: Erb Valve')
            start_erb_thread('pericardial_rub')
        elif 'graham_steell_murmur_sound_erb_point' in request.POST:
            print('\nSound Played: Graham Steell Murmur, Location: Erb Valve')
            start_erb_thread('pericardial_rub')
        elif 'aortic_valve_regurgitation_sound_erb_point' in request.POST:
            print('\nSound Played: Aortic Valve Regurgitation, Location: Erb Valve')
            start_erb_thread('aortic_valve_regurgitation')
        elif 'aortic_valve_stenosis_sound_erb_point' in request.POST:
            print('\nSound Played: Aortic Valve Stenosis, Location: Erb Valve')
            start_erb_thread('aortic_valve_stenosis')
        elif 'aortic_valve_stenosis_regurgitation_sound_erb_point' in request.POST:
            print('\nSound Played: Aortic Valve Stenosis Regurgitation, Location: Erb Valve')
            start_erb_thread('aortic_stenosis_regurgitation')
        elif 'congenital_aortic_stenosis_sound_erb_point' in request.POST:
            print('\nSound Played: Congenital Aortic Stenosis, Location: Erb Valve')
            start_erb_thread('congenital_aortic_stenosis')
        elif 'mitral_valve_regurgitation_sound_erb_point' in request.POST:
            print('\nSound Played: Mitral Valve Regurgitation, Location: Erb Valve')
            start_erb_thread('mitral_valve_regurgitation')
        elif 'mitral_valve_stenosis_sound_erb_point' in request.POST:
            print('\nSound Played: Mitral Valve Stenosis, Location: Erb Valve')
            start_erb_thread('mitral_valve_stenosis')
        elif 'mitral_valve_prelapse_sound_erb_point' in request.POST:
            print('\nSound Played: Mitral Valve Prelapse, Location: Erb Valve')
            start_erb_thread('mitral_valve_prelapse')
        elif 'mitral_stenosis_regurgitation_sound_erb_point' in request.POST:
            print('\nSound Played: Mitral Stenosis Regurgitation, Location: Erb Valve')
            start_erb_thread('mitral_stenosis_regurgitation')
        elif 'mitral_stenosis_tricuspid_regurgitation_sound_erb_point' in request.POST:
            print('\nSound Played: Mitral Stenosis Tricuspid Regurgitation, Location: Erb Valve')
            start_erb_thread('mitral_stenosis_tricuspid_regurgitation')
        elif 'pulmonary_valve_stenosis_sound_erb_point' in request.POST:
            print('\nSound Played: Pulmonary Valve Stenosis, Location: Erb Valve')
            start_erb_thread('pulmonary_valve_stenosis')
        elif 'pulmonary_valve_regurgitation_sound_erb_point' in request.POST:
            print('\nSound Played: Pulmonary Valve Regurgitation, Location: Erb Valve')
            start_erb_thread('pulmonary_valve_regurgitation')
        elif 'tricuspid_valve_regurgitation_sound_erb_point' in request.POST:
            print('\nSound Played: Tricuspid Valve Regurgitation, Location: Erb Valve')
            start_erb_thread('tricuspid_valve_regurgitation')
        elif 'coarctation_of_the_aorta_sound_erb_valve' in request.POST:
            print('\nSound Played: Coarctation of the Aorta, Location: Erb Valve')
            start_erb_thread('coarctation_of_the_aorta')
        elif 'hypertrophic_cardiomyopathy_sound_erb_valve' in request.POST:
            print('\nSound Played: Hypertrophic Cardiomyopathy, Location: Erb Valve')
            start_erb_thread('hypertrophic_cardiomyopathy')
        elif 'patent_ductus_arteriosus_sound_erb_valve' in request.POST:
            print('\nSound Played: Patent Ductus Arteriosus, Location: Erb Valve')
            start_erb_thread('patent_ductus_arteriosus')
        elif 'atrial_septal_defect_sound_erb_valve' in request.POST:
            print('\nSound Played: Atrial Septal Defect, Location: Erb Valve')
            start_erb_thread('atrial_septal_defect')
        elif 'ventricular_septal_defect_sound_erb_valve' in request.POST:
            print('\nSound Played: Ventricular Septal Defect, Location: Erb Valve')
            start_erb_thread('ventricular_septal_defect')
        elif 'acute_myocardial_infarction_sound_erb_valve' in request.POST:
            print('\nSound Played: Acute Myocardial Infaction, Location: Erb Valve')
            start_erb_thread('acute_myocardial_infarction')
        elif 'congestive_heart_failure_sound_erb_valve' in request.POST:
            print('\nSound Played: Congestive Heart Failure, Location: Erb Valve')
            start_erb_thread('congestive_heart_failure')
        elif 'systemic_hypertension_sound_erb_valve' in request.POST:
            print('\nSound Played: Systemic Hypertension, Location: Erb Valve')
            start_erb_thread('systemic_hypertension')
        elif 'acute_pericarditis_sound_erb_valve' in request.POST:
            print('\nSound Played: Acute Pericarditis, Location: Erb Valve')
            start_erb_thread('acute_pericarditis')
        elif 'dilated_cardiomyopathy_sound_erb_valve' in request.POST:
            print('\nSound Played: Dilated Cardiomyopathy, Location: Erb Valve')
            start_erb_thread('dilated_cardiomyopathy')
        elif 'pulmonary_hypertension_sound_erb_valve' in request.POST:
            print('\nSound Played: Pulmonary Hypertension, Location: Erb Valve')
            start_erb_thread('pulmonary_hypertension')
        elif 'tetralogy_of_fallot_sound_erb_valve' in request.POST:
            print('\nSound Played: Tetralogy of Fallot, Location: Erb Valve')
            start_erb_thread('tetralogy_of_fallot')
        elif 'ventricular_aneurysm_sound_erb_valve' in request.POST:
            print('\nSound Played: Ventricular Aneurysm, Location: Erb Valve')
            start_erb_thread('ventricular_aneurysm')
        elif 'ebstein_anomaly_sound_erb_valve' in request.POST:
            print('\nSound Played: Ebstein Anomaly, Location: Erb Valve')
            start_erb_thread('ebsteins_anomaly')
        return JsonResponse({'message': 'Success!'})
    else:
        return HttpResponse("Request method is not a POST")

# Create your views here.
def index(request):
    global hr_show, rr_show

    print('Heart Rate is: {}, Breadth Rate is: {}'.format(hr_show, rr_show))
    context = {
        'hr_show': hr_show,
        'rr_show': rr_show
    }
    
    return render(request, 'index.html', context)