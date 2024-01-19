from urllib import request
from django.http import JsonResponse
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
    if request.method == 'POST':
        if 'hr_plus' in request.POST:
            hr_show += 1
        elif 'hr_minus' in request.POST:
            hr_show -= 1
        elif 'rr_plus' in request.POST:
            rr_show += 1
        elif 'rr_minus' in request.POST:
            rr_show -= 1
        else:
            hr_show += 0
            rr_show += 0
        context = {
            'hr_show': hr_show,
            'rr_show': rr_show
        }
    else:
        context = {
            'hr_show': hr_show,
            'rr_show': rr_show
        }
    return render(request, 'heart.html', context)

def test(request):
    if request.method == 'POST':
        form = heartAudioForms(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = heartAudioForms()

    return render(request, 'test.html', {'form': form})