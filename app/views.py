from urllib import request
from django.http import JsonResponse
from django.shortcuts import render, redirect
import time
from playsound import playsound

from .models import heartAudio, lungAudio
from .forms import heartAudioForms, lungAudioForm
from .DashApp import ecg_dash, rsp_dash, hbr_dash, comp_dash

# Create your views here.
def index_heart(request):
    return render(request, 'heart.html', context={})

def test(request):
    if request.method == 'POST':
        form = heartAudioForms(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = heartAudioForms()

    return render(request, 'test.html', {'form': form})