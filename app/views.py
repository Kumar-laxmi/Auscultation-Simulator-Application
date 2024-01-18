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
    if request.method == 'POST':
        action = request.POST.get('action')
        current_hr = request.session.get('current_hr', 60)

        # Update the heart rate based on the action
        if action == 'increase':
            current_hr += 1
            print(current_hr)
        elif action == 'decrease':
            current_hr -= 1
            print(current_hr)

        # Return the updated heart rate as JSON
        return JsonResponse({'current_hr': current_hr})
    else:
        current_hr = request.session.get('current_hr', 60)
        print(current_hr)
        context = {'current_hr': current_hr}
        return render(request, 'heart.html', context)

def test(request):
    if request.method == 'POST':
        form = heartAudioForms(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = heartAudioForms()

    return render(request, 'test.html', {'form': form})