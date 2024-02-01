from django.shortcuts import render
from django.views import View
from django.http import JsonResponse, HttpResponse
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

class AuscultationView(View):
    template_name = 'index.html'

    def get_context_data(self):
        global hr_show, rr_show
        context = {'hr_show': hr_show, 'rr_show': rr_show}
        return context

    def play_audio(self, index, samples, samplerate, stop_flag):
        global speakers
        while not stop_flag.is_set():
            speaker = speakers[index]
            speaker.play(samples, samplerate)

    def update_rate(self, request, rate_type, rate_variable, update_value):
        global con, cursor
        if request.method == 'POST':
            cursor = con.cursor()
            rate_variable += update_value
            cursor.execute(f"""UPDATE {rate_type} SET {rate_type} = {rate_variable} WHERE default_col=1""")
            con.commit()
            print(f'\n{rate_type} updated to: {rate_variable}')
            cursor.close()
            return JsonResponse({'message': 'Success!', f'{rate_type}_show': rate_variable})
        else:
            return HttpResponse("Request method is not a POST")

    def heart_update(self, request):
        global hr_show
        return self.update_rate(request, 'heartrate', hr_show, 0)

    def breath_update(self, request):
        global rr_show
        return self.update_rate(request, 'breathrate', rr_show, 0)

    def post(self, request):
        global hr_show, rr_show

        global current_audio_stream_mitral, current_audio_stream_aortic, current_audio_stream_pulmonary, current_audio_stream_tricuspid, current_audio_stream_erb
        global playing_thread_mitral, playing_thread_aortic, playing_thread_pulmonary, playing_thread_tricuspid, playing_thread_erb
        global stop_flag_mitral, stop_flag_aortic, stop_flag_pulmonary, stop_flag_tricuspid, stop_flag_erb

        try:
            con = sqlite3.connect("/home/pi/Downloads/Auscultation-Simulator-Application/app/sounds.sqlite3", check_same_thread=False)
        except:
            con = sqlite3.connect("/Users/kumarlaxmikant/Desktop/Visual_Studio/Auscultation-Simulator-Application/app/sounds.sqlite3", check_same_thread=False)
        df_heart = pd.read_sql_query("SELECT * FROM app_heartaudio", con)

        context = self.get_context_data()

        if request.method == 'POST':
            rate_update_methods = {
                'heart': self.heart_update,
                'breath': self.breath_update
            }
            rate_type = request.POST.get('rate_type', None)
            if rate_type in rate_update_methods:
                return rate_update_methods[rate_type](request)

            if current_audio_stream_mitral:
                if playing_thread_mitral and playing_thread_mitral.is_alive():
                    stop_flag_mitral.set()
                    playing_thread_mitral.join()
                current_audio_stream_mitral = False

            # Continue with other valve checks...

            context['message'] = 'Success'
        else:
            print('Heart Rate is: {}, Breath Rate is: {}'.format(hr_show, rr_show))
            cursor.execute("""UPDATE heartrate SET heartrate = '60'""")
            con.commit()
            cursor.execute("""UPDATE breathrate SET breathrate = '15'""")
            con.commit()

        return render(request, self.template_name, context)

    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context)
