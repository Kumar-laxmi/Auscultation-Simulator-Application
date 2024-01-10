from urllib import request
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
import time
from playsound import playsound

from .DashApp import ecg_dash, rsp_dash

hr_show = ecg_dash.hr_show
rr_show = rsp_dash.rr_show

# Create your views here.
def index(request):
    global hr_show
    global rr_show
    # Updating the Heart Rate and Respiration Rate graph
    if request.method == "POST":
        hr_show = int(request.form.get('hr_show'))
        print(hr_show)
        ecg_dash.hr_show = hr_show
        rr_show = int(request.form.get('rr_show'))
        rsp_dash.rr_show = rr_show

    return render(request, 'heart.html', {})