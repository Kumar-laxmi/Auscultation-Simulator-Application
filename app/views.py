from urllib import request
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
import soundcard as sc
import soundfile as sf
from pydub import AudioSegment
import sqlite3
import pandas as pd
import threading

from .models import heartAudio, lungAudio
from .forms import heartAudioForms, lungAudioForm
from .DashApp import ecg_dash, rsp_dash, hbr_dash, comp_dash

# Define the signal
hr_show, rr_show = 60, 15   # Initialize the Heart Rate and Breadth Rate

speakers = sc.all_speakers()

try:
    con = sqlite3.connect("/home/pi/Downloads/Auscultation-Simulator-Application/app/sounds.sqlite3", check_same_thread=False)
except:
    con = sqlite3.connect("/Users/kumarlaxmikant/Desktop/Visual_Studio/Auscultation-Simulator-Application/app/sounds.sqlite3", check_same_thread=False)
df_heart = pd.read_sql_query("SELECT * FROM app_heartaudio", con)

heart_tones = ["normal_heart_sound","split_first_heart_sound","split_second_heart_sound","third_heart_sound","fourth_heart_sound"]
murmurs = ["functional_murmur_sound", "diastolic_murmur_sound", "opening_snap_sound", "holosystolic_murmur_sound", "early_systolic_murmur_sound", "mid_systolic_murmur_sound", "continuous_murmur_sound", "austin_flint_murmur_sound", "pericardial_rub_sound", "graham_steell_murmur_sound"]
aortic_valve = ["aortic_valve_regurgitation_sound","aortic_valve_stenosis_sound","aortic_valve_stenosis_regurgitation_sound","congenital_aortic_stenosis_sound"]
mitral_valve = ["mitral_valve_regurgitation_sound","mitral_valve_stenosis_sound","mitral_valve_prelapse_sound","mitral_stenosis_regurgitation_sound","mitral_stenosis_tricuspid_regurgitation_sound"]
pulmonary_valve = ["pulmonary_valve_stenosis_sound","pulmonary_valve_regurgitation_sound"]
tricuspid_valve = ["tricuspid_valve_regurgitation_sound"]
pathology = ["coarctation_of_the_aorta_sound","hypertrophic_cardiomyopathy_sound","patent_ductus_arteriosus_sound","atrial_septal_defect_sound","ventricular_septal_defect_sound","acute_myocardial_infarction_sound","congestive_heart_failure_sound","systemic_hypertension_sound","acute_pericarditis_sound","dilated_cardiomyopathy_sound","pulmonary_hypertension_sound","tetralogy_of_fallot_sound","ventricular_aneurysm_sound","ebstein_anomaly_sound"]

original_sounds = heart_tones + murmurs + aortic_valve + mitral_valve + pulmonary_valve + tricuspid_valve + pathology

current_audio_stream_mitral, current_audio_stream_aortic, current_audio_stream_pulmonary, current_audio_stream_tricuspid, current_audio_stream_erb = False, False, False, False, False
playing_thread_mitral, playing_thread_aortic, playing_thread_pulmonary, playing_thread_tricuspid, playing_thread_erb = None, None, None, None, None
stop_flag_mitral, stop_flag_aortic, stop_flag_pulmonary, stop_flag_tricuspid, stop_flag_erb = threading.Event(), threading.Event(), threading.Event(), threading.Event(), threading.Event()

def play_mitral(index, samples, samplerate):
    global speakers, stop_flag_mitral
    while not stop_flag_mitral.is_set():
        speaker = speakers[index]
        speaker.play(samples, samplerate)

def play_aortic(index, samples, samplerate):
    global speakers, stop_flag_aortic
    while not stop_flag_aortic.is_set():
        speaker = speakers[index]
        speaker.play(samples, samplerate)

def play_pulmonary(index, samples, samplerate):
    global speakers, stop_flag_pulmonary
    while not stop_flag_pulmonary.is_set():
        speaker = speakers[index]
        speaker.play(samples, samplerate)

def play_tricuspid(index, samples, samplerate):
    global speakers, stop_flag_tricuspid
    while not stop_flag_tricuspid.is_set():
        speaker = speakers[index]
        speaker.play(samples, samplerate)

def play_erb(index, samples, samplerate):
    global speakers, stop_flag_erb
    while not stop_flag_erb.is_set():
        speaker = speakers[index]
        speaker.play(samples, samplerate)
        
def heartUpdate(request):
    global hr_show

    if request.method == 'POST':
        if 'hr_plus' in request.POST:
            hr_show += 1
            print('\nHeart Rate updated to: {}'.format(hr_show))
        elif 'hr_minus' in request.POST:
            hr_show -= 1
            print('\nHeart Rate updated to: {}'.format(hr_show))
        else:
            hr_show += 0
        return JsonResponse({'message': 'Success!', 'hr_show': hr_show})
    else:
        return HttpResponse("Request method is not a POST")

def breathUpdate(request):
    global rr_show

    if request.method == 'POST':
        if 'rr_plus' in request.POST:
            rr_show += 1
            print('\nBreath Rate updated to: {}'.format(rr_show))
        elif 'rr_minus' in request.POST:
            rr_show -= 1
            print('\nBreath Rate updated to: {}'.format(rr_show))
        else:
            rr_show += 0
        return JsonResponse({'message': 'Success!', 'rr_show': rr_show})
    else:
        return HttpResponse("Request method is not a POST")

def start_mitral_thread(sound_name):
    global playing_thread_mitral, stop_flag_mitral, hr_show
    if playing_thread_mitral and playing_thread_mitral.is_alive():
        stop_flag_mitral.set()  # Set the reload flag to signal the thread to stop
        playing_thread_mitral.join()
        print('Destroyed Mitral thread')
        stop_flag_mitral = threading.Event()

    # Start a new thread
    data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == sound_name) & (df_heart['sound_type'] == 'M'), 'audio_file_path'].values[0])
    playing_thread_mitral = threading.Thread(target=play_mitral, args=(1, data, fs))
    playing_thread_mitral.start()

def start_aortic_thread(sound_name):
    global playing_thread_aortic, stop_flag_aortic, hr_show
    if playing_thread_aortic and playing_thread_aortic.is_alive():
        stop_flag_aortic.set()  # Set the reload flag to signal the thread to stop
        playing_thread_aortic.join()
        print('Destroyed Aortic thread')
        stop_flag_aortic = threading.Event()

    # Start a new thread
    data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == sound_name) & (df_heart['sound_type'] == 'A'), 'audio_file_path'].values[0])
    playing_thread_aortic = threading.Thread(target=play_aortic, args=(2, data, fs))
    playing_thread_aortic.start()

def start_pulmonary_thread(sound_name):
    global playing_thread_pulmonary, stop_flag_pulmonary, hr_show
    if playing_thread_pulmonary and playing_thread_pulmonary.is_alive():
        stop_flag_pulmonary.set()  # Set the reload flag to signal the thread to stop
        playing_thread_pulmonary.join()
        print('Destroyed Pulmonary thread')
        stop_flag_pulmonary = threading.Event()

    # Start a new thread
    data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == sound_name) & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
    playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
    playing_thread_pulmonary.start()

def start_tricuspid_thread(sound_name):
    global playing_thread_tricuspid, stop_flag_tricuspid, hr_show
    if playing_thread_tricuspid and playing_thread_tricuspid.is_alive():
        stop_flag_tricuspid.set()  # Set the reload flag to signal the thread to stop
        playing_thread_tricuspid.join()
        print('Destroyed Tricuspid thread')
        stop_flag_tricuspid = threading.Event()

    # Start a new thread
    data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == sound_name) & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
    playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
    playing_thread_tricuspid.start()

def start_erb_thread(sound_name):
    global playing_thread_erb, stop_flag_erb, hr_show
    if playing_thread_erb and playing_thread_erb.is_alive():
        stop_flag_erb.set()  # Set the reload flag to signal the thread to stop
        playing_thread_erb.join()
        print('Destroyed Erb thread')
        stop_flag_erb = threading.Event()

    # Start a new thread
    data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == sound_name) & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
    playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
    playing_thread_erb.start()

# Create your views here.
def index(request):
    global hr_show, rr_show, original_sounds
    global current_audio_stream_mitral, current_audio_stream_aortic, current_audio_stream_pulmonary, current_audio_stream_tricuspid, current_audio_stream_erb
    global playing_thread_mitral, playing_thread_aortic, playing_thread_pulmonary, playing_thread_tricuspid, playing_thread_erb
    global stop_flag_mitral, stop_flag_aortic, stop_flag_pulmonary, stop_flag_tricuspid, stop_flag_erb

    suffix1, suffix2, suffix3, suffix4, suffix5 = "_mitral_valve","_aortic_valve","_pulmonary_valve","_tricuspid_valve","_erb_point"

    global df_heart

    if request.method == 'POST':
        current_audio_stream_mitral = any(x in [sound + suffix1 for sound in original_sounds] for x in request.POST)
        current_audio_stream_aortic = any(x in [sound + suffix2 for sound in original_sounds] for x in request.POST)
        current_audio_stream_pulmonary = any(x in [sound + suffix3 for sound in original_sounds] for x in request.POST)
        current_audio_stream_tricuspid = any(x in [sound + suffix4 for sound in original_sounds] for x in request.POST)
        current_audio_stream_erb = any(x in [sound + suffix5 for sound in original_sounds] for x in request.POST)
        
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
            start_mitral_thread('normal_heart')
        elif 'split_first_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Split First Heart, Location: Mitral Valve')
            start_mitral_thread('split_first_heart_sound')
        elif 'split_second_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Mitral Valve')
            start_mitral_thread('split_second_heart_sound')
        elif 'third_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Third Heart (gallop), Location: Mitral Valve')
            start_mitral_thread('third_heart_sound_gallop')
        elif 'fourth_heart_sound_mitral_valve' in request.POST:
            print('\nSound Played: Fourth Heart (gallop), Location: Mitral Valve')
            start_mitral_thread('fourth_heart_sound_gallop')
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
            start_mitral_thread('aortic_valve_stenosis')
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
            start_mitral_thread('mitral_valve_prolapse')
        elif 'mitral_stenosis_regurgitation_sound_mitral_valve' in request.POST:
            print('\nSound Played: Mitral Stenosis Regurgitation, Location: Mitral Valve')
            start_mitral_thread('mitral_stenosis_and_regurgitation')
        elif 'mitral_stenosis_tricuspid_regurgitation_sound_mitral_valve' in request.POST:
            print('\nSound Played: Mitral Stenosis Tricuspid Regurgitation, Location: Mitral Valve')
            start_mitral_thread('mitral_stenosis_and_tricuspid_regurgitation')
        elif 'pulmonary_valve_stenosis_sound_mitral_valve' in request.POST:
            print('\nSound Played: Pulmonary Valve Stenosis, Location: Mitral Valve')
            start_mitral_thread('pulmonary_valve_stenosis')
        elif 'pulmonary_valve_regurgitation_sound_mitral_valve' in request.POST:
            print('\nSound Played: Pulmonary Valve Regurgitation, Location: Mitral Valve')
            start_mitral_thread('pulmonary_valve_regurgitation')
        elif 'tricuspid_valve_regurgitation_sound_mitral_valve' in request.POST:
            print('\nSound Played: Tricuspid Valve Regurgitation, Location: Mitral Valve')
            start_mitral_thread('tricuspid_valve_regurgitation')
        
        # "coarctation_of_the_aorta_sound_mitral_valve","hypertrophic_cardiomyopathy_sound_mitral_valve","patent_ductus_arteriosus_sound_mitral_valve"
        # "atrial_septal_defect_sound_mitral_valve","ventricular_septal_defect_sound_mitral_valve","acute_myocardial_infarction_sound_mitral_valve"
        # "congestive_heart_failure_sound_mitral_valve","systemic_hypertension_sound_mitral_valve","acute_pericarditis_sound_mitral_valve"
        # "dilated_cardiomyopathy_sound_mitral_valve","pulmonary_hypertension_sound_mitral_valve","tetralogy_of_fallot_sound_mitral_valve"
        # "ventricular_aneurysm_sound_mitral_valve","ebstein_anomaly_sound_mitral_valve"

        # Buttons for Aortic Valve
        if 'normal_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Normal Heart, Location: Aortic Valve')
            start_aortic_thread('normal_heart')
        elif 'split_first_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Split First Heart, Location: Aortic Valve')
            start_aortic_thread('split_first_heart_sound')
        elif 'split_second_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Aortic Valve')
            start_aortic_thread('split_second_heart_sound')
        elif 'third_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Third Heart (gallop), Location: Aortic Valve')
            start_aortic_thread('third_heart_sound_gallop')
        elif 'fourth_heart_sound_aortic_valve' in request.POST:
            print('\nSound Played: Fourth Heart (gallop), Location: Aortic Valve')
            start_aortic_thread('fourth_heart_sound_gallop')
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
            start_aortic_thread('aortic_stenosis_and_regurgitation')
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
            start_aortic_thread('mitral_valve_prolapse')
        elif 'mitral_stenosis_regurgitation_sound_aortic_valve' in request.POST:
            print('\nSound Played: Mitral Stenosis Regurgitation, Location: Aortic Valve')
            start_aortic_thread('mitral_stenosis_and_regurgitation')
        elif 'mitral_stenosis_tricuspid_regurgitation_sound_aortic_valve' in request.POST:
            print('\nSound Played: Mitral Stenosis Tricuspid Regurgitation, Location: Aortic Valve')
            start_aortic_thread('mitral_stenosis_and_tricuspid_regurgitation')
        elif 'pulmonary_valve_stenosis_sound_aortic_valve' in request.POST:
            print('\nSound Played: Pulmonary Valve Stenosis, Location: Aortic Valve')
            start_aortic_thread('pulmonary_valve_stenosis')
        elif 'pulmonary_valve_regurgitation_sound_aortic_valve' in request.POST:
            print('\nSound Played: Pulmonary Valve Regurgitation, Location: Aortic Valve')
            start_aortic_thread('pulmonary_valve_regurgitation')
        elif 'tricuspid_valve_regurgitation_sound_aortic_valve' in request.POST:
            print('\nSound Played: Tricuspid Valve Regurgitation, Location: Aortic Valve')
            start_aortic_thread('tricuspid_valve_regurgitation')
            
        # "coarctation_of_the_aorta_sound_aortic_valve","hypertrophic_cardiomyopathy_sound_aortic_valve","patent_ductus_arteriosus_sound_aortic_valve"
        # "atrial_septal_defect_sound_aortic_valve","ventricular_septal_defect_sound_aortic_valve","acute_myocardial_infarction_sound_aortic_valve"
        # "congestive_heart_failure_sound_aortic_valve","systemic_hypertension_sound_aortic_valve","acute_pericarditis_sound_aortic_valve"
        # "dilated_cardiomyopathy_sound_aortic_valve","pulmonary_hypertension_sound_aortic_valve","tetralogy_of_fallot_sound_aortic_valve"
        # "ventricular_aneurysm_sound_aortic_valve","ebstein_anomaly_sound_aortic_valve"
        
        # Buttons for Pulmonary Valve
        if 'normal_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Normal Heart, Location: Pulmonary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'split_first_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Split First Heart, Location: Pulmonary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_first_heart_sound') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'split_second_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_second_heart_sound') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'third_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Third Heart (gallop), Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'third_heart_sound_gallop') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'fourth_heart_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Fourth Heart (gallop), Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'fourth_heart_sound_gallop') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'functional_murmur_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Functional Murmur, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'functional_murmur') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'diastolic_murmur_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Diastolic Murmur, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'diastolic_murmur') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'opening_snap_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Opening Snap, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'opening_snap') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'holosystolic_murmur_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Holosystolic Murmur, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'holosystolic_murmur') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'early_systolic_murmur_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Early Systolic Murmur, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'early_systolic_murmur') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'mid_systolic_murmur_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Mid Systolic Murmur, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mid_systolic_murmur') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'continuous_murmur_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Continuous Murmur, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'continuous_murmur') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'austin_flint_murmur_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Austin Flint Murmur, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'austin_flint_murmur') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'pericardial_rub_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Pericardial Rub, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'pericardial_rub') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'graham_steell_murmur_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Graham Steell Murmur, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'pericardial_rub') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'aortic_valve_regurgitation_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Aortic Valve Regurgitation, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'aortic_valve_regurgitation') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'aortic_valve_stenosis_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Aortic Valve Stenosis, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'aortic_valve_stenosis') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'aortic_valve_stenosis_regurgitation_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Aortic Valve Stenosis Regurgitation, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'aortic_valve_stenosis') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'congenital_aortic_stenosis_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Congenital Aortic Stenosis, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'congenital_aortic_stenosis') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'mitral_valve_regurgitation_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Mitral Valve Regurgitation, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mitral_valve_regurgitation') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'mitral_valve_stenosis_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Mitral Valve Stenosis, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mitral_valve_stenosis') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'mitral_valve_prelapse_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Mitral Valve Prelapse, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mitral_valve_prolapse') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'mitral_stenosis_regurgitation_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Mitral Stenosis Regurgitation, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mitral_stenosis_and_regurgitation') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'mitral_stenosis_tricuspid_regurgitation_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Mitral Stenosis Tricuspid Regurgitation, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mitral_stenosis_and_tricuspid_regurgitation') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'pulmonary_valve_stenosis_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Pulmonary Valve Stenosis, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'pulmonary_valve_stenosis') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'pulmonary_valve_regurgitation_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Pulmonary Valve Regurgitation, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'pulmonary_valve_regurgitation') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        elif 'tricuspid_valve_regurgitation_sound_pulmonary_valve' in request.POST:
            print('\nSound Played: Tricuspid Valve Regurgitation, Location: Pulmonanary Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'tricuspid_valve_regurgitation') & (df_heart['sound_type'] == 'P'), 'audio_file_path'].values[0])
            playing_thread_pulmonary = threading.Thread(target=play_pulmonary, args=(3, data, fs))
            playing_thread_pulmonary.start()
        
        # "coarctation_of_the_aorta_sound_pulmonary_valve","hypertrophic_cardiomyopathy_sound_pulmonary_valve","patent_ductus_arteriosus_sound_pulmonary_valve"
        # "atrial_septal_defect_sound_pulmonary_valve","ventricular_septal_defect_sound_pulmonary_valve","acute_myocardial_infarction_sound_pulmonary_valve"
        # "congestive_heart_failure_sound_pulmonary_valve","systemic_hypertension_sound_pulmonary_valve","acute_pericarditis_sound_pulmonary_valve"
        # "dilated_cardiomyopathy_sound_pulmonary_valve","pulmonary_hypertension_sound_pulmonary_valve","tetralogy_of_fallot_sound_pulmonary_valve"
        # "ventricular_aneurysm_sound_pulmonary_valve","ebstein_anomaly_sound_pulmonary_valve"

        # Buttons for Tricuspid Valve
        if 'normal_heart_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Normal Heart, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'normal_heart') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'split_first_heart_sound_tricuspid_valvee' in request.POST:
            print('\nSound Played: Split First Heart, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_first_heart_sound') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'split_second_heart_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Split Second Heart, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'split_second_heart_sound') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'third_heart_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Third Heart (gallop), Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'third_heart_sound_gallop') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'fourth_heart_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Fourth Heart (gallop), Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'fourth_heart_sound_gallop') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'functional_murmur_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Functional Murmur, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'functional_murmur') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'diastolic_murmur_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Diastolic Murmur, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'diastolic_murmur') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'opening_snap_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Opening Snap, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'opening_snap') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'holosystolic_murmur_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Holosystolic Murmur, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'holosystolic_murmur') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'early_systolic_murmur_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Early Systolic Murmur, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'early_systolic_murmur') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'mid_systolic_murmur_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Mid Systolic Murmur, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mid_systolic_murmur') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'continuous_murmur_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Continuous Murmur, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'continuous_murmur') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'austin_flint_murmur_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Austin Flint Murmur, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'austin_flint_murmur') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'pericardial_rub_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Pericardial Rub, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'pericardial_rub') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'graham_steell_murmur_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Graham Steell Murmur, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'pericardial_rub') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'aortic_valve_regurgitation_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Aortic Valve Regurgitation, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'aortic_valve_regurgitation') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'aortic_valve_stenosis_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Aortic Valve Stenosis, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'aortic_valve_stenosis') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'aortic_valve_stenosis_regurgitation_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Aortic Valve Stenosis Regurgitation, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'aortic_valve_stenosis') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'congenital_aortic_stenosis_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Congenital Aortic Stenosis, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'congenital_aortic_stenosis') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'mitral_valve_regurgitation_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Mitral Valve Regurgitation, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mitral_valve_regurgitation') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'mitral_valve_stenosis_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Mitral Valve Stenosis, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mitral_valve_stenosis') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'mitral_valve_prelapse_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Mitral Valve Prelapse, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mitral_valve_prolapse') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'mitral_stenosis_regurgitation_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Mitral Stenosis Regurgitation, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mitral_stenosis_and_regurgitation') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'mitral_stenosis_tricuspid_regurgitation_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Mitral Stenosis Tricuspid Regurgitation, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mitral_stenosis_and_tricuspid_regurgitation') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'pulmonary_valve_stenosis_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Pulmonary Valve Stenosis, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'pulmonary_valve_stenosis') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'pulmonary_valve_regurgitation_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Pulmonary Valve Regurgitation, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'pulmonary_valve_regurgitation') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        elif 'tricuspid_valve_regurgitation_sound_tricuspid_valve' in request.POST:
            print('\nSound Played: Tricuspid Valve Regurgitation, Location: Tricuspid Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'tricuspid_valve_regurgitation') & (df_heart['sound_type'] == 'T'), 'audio_file_path'].values[0])
            playing_thread_tricuspid = threading.Thread(target=play_tricuspid, args=(4, data, fs))
            playing_thread_tricuspid.start()
        
        # "coarctation_of_the_aorta_sound_tricuspid_valve","hypertrophic_cardiomyopathy_sound_tricuspid_valve","patent_ductus_arteriosus_sound_tricuspid_valve"
        # "atrial_septal_defect_sound_tricuspid_valve","ventricular_septal_defect_sound_tricuspid_valve","acute_myocardial_infarction_sound_tricuspid_valve"
        # "congestive_heart_failure_sound_tricuspid_valve","systemic_hypertension_sound_tricuspid_valve","acute_pericarditis_sound_tricuspid_valve"
        # "dilated_cardiomyopathy_sound_tricuspid_valve","pulmonary_hypertension_sound_tricuspid_valve","tetralogy_of_fallot_sound_tricuspid_valve"
        # "ventricular_aneurysm_sound_tricuspid_valve","ebstein_anomaly_sound_tricuspid_valve"
        
        # Buttons for Erb Point Valve
        if 'normal_heart_sound_erb_point' in request.POST:
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
        elif 'functional_murmur_sound_erb_point' in request.POST:
            print('\nSound Played: Functional Murmur, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'functional_murmur') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'diastolic_murmur_sound_erb_point' in request.POST:
            print('\nSound Played: Diastolic Murmur, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'diastolic_murmur') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'opening_snap_sound_erb_point' in request.POST:
            print('\nSound Played: Opening Snap, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'opening_snap') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'holosystolic_murmur_sound_erb_point' in request.POST:
            print('\nSound Played: Holosystolic Murmur, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'holosystolic_murmur') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'early_systolic_murmur_sound_erb_point' in request.POST:
            print('\nSound Played: Early Systolic Murmur, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'early_systolic_murmur') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'mid_systolic_murmur_sound_erb_point' in request.POST:
            print('\nSound Played: Mid Systolic Murmur, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mid_systolic_murmur') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'continuous_murmur_sound_erb_point' in request.POST:
            print('\nSound Played: Continuous Murmur, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'continuous_murmur') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'austin_flint_murmur_sound_erb_point' in request.POST:
            print('\nSound Played: Austin Flint Murmur, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'austin_flint_murmur') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'pericardial_rub_sound_erb_point' in request.POST:
            print('\nSound Played: Pericardial Rub, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'pericardial_rub') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'graham_steell_murmur_sound_erb_point' in request.POST:
            print('\nSound Played: Graham Steell Murmur, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'pericardial_rub') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'aortic_valve_regurgitation_sound_erb_point' in request.POST:
            print('\nSound Played: Aortic Valve Regurgitation, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'aortic_valve_regurgitation') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'aortic_valve_stenosis_sound_erb_point' in request.POST:
            print('\nSound Played: Aortic Valve Stenosis, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'aortic_valve_stenosis') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'aortic_valve_stenosis_regurgitation_sound_erb_point' in request.POST:
            print('\nSound Played: Aortic Valve Stenosis Regurgitation, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'aortic_valve_stenosis') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'congenital_aortic_stenosis_sound_erb_point' in request.POST:
            print('\nSound Played: Congenital Aortic Stenosis, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'congenital_aortic_stenosis') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'mitral_valve_regurgitation_sound_erb_point' in request.POST:
            print('\nSound Played: Mitral Valve Regurgitation, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mitral_valve_regurgitation') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'mitral_valve_stenosis_sound_erb_point' in request.POST:
            print('\nSound Played: Mitral Valve Stenosis, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mitral_valve_stenosis') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'mitral_valve_prelapse_sound_erb_point' in request.POST:
            print('\nSound Played: Mitral Valve Prelapse, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mitral_valve_prolapse') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'mitral_stenosis_regurgitation_sound_erb_point' in request.POST:
            print('\nSound Played: Mitral Stenosis Regurgitation, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mitral_stenosis_and_regurgitation') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'mitral_stenosis_tricuspid_regurgitation_sound_erb_point' in request.POST:
            print('\nSound Played: Mitral Stenosis Tricuspid Regurgitation, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'mitral_stenosis_and_tricuspid_regurgitation') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'pulmonary_valve_stenosis_sound_erb_point' in request.POST:
            print('\nSound Played: Pulmonary Valve Stenosis, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'pulmonary_valve_stenosis') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'pulmonary_valve_regurgitation_sound_erb_point' in request.POST:
            print('\nSound Played: Pulmonary Valve Regurgitation, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'pulmonary_valve_regurgitation') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        elif 'tricuspid_valve_regurgitation_sound_erb_point' in request.POST:
            print('\nSound Played: Tricuspid Valve Regurgitation, Location: Erb Valve')
            data, fs = sf.read(df_heart.loc[(df_heart['sound_name'] == 'tricuspid_valve_regurgitation') & (df_heart['sound_type'] == 'E'), 'audio_file_path'].values[0])
            playing_thread_erb = threading.Thread(target=play_erb, args=(5, data, fs))
            playing_thread_erb.start()
        
        # "coarctation_of_the_aorta_sound_erb_point","hypertrophic_cardiomyopathy_sound_erb_point","patent_ductus_arteriosus_sound_erb_point"
        # "atrial_septal_defect_sound_erb_point","ventricular_septal_defect_sound_erb_point","acute_myocardial_infarction_sound_erb_point"
        # "congestive_heart_failure_sound_erb_point","systemic_hypertension_sound_erb_point","acute_pericarditis_sound_erb_point"
        # "dilated_cardiomyopathy_sound_erb_point","pulmonary_hypertension_sound_erb_point","tetralogy_of_fallot_sound_erb_point"
        # "ventricular_aneurysm_sound_erb_point","ebstein_anomaly_sound_erb_point"

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