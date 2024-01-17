from urllib import request
from django.shortcuts import render, redirect
import time
from playsound import playsound

from .models import heartAudio, lungAudio
from .forms import heartAudioForms, lungAudioForm
from .DashApp import ecg_dash, rsp_dash, hbr_dash, comp_dash

hr_show = 60
rr_show = 15

# Create your views here.
def index_heart(request):
    global hr_show
    global rr_show
    # Updating the Heart Rate and Respiration Rate graph
    if request.method == "POST":
        hr_show = int(request.form.get('hr_show'))
        print(hr_show)
        rr_show = int(request.form.get('rr_show'))
        print(rr_show)

    return render(request, 'heart.html', {})

def test(request):
    if request.method == 'POST':
        form = heartAudioForms(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = heartAudioForms()

    return render(request, 'test.html', {'form': form})