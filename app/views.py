from urllib import request
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext

import plotly.graph_objects as go
from plotly.offline import plot
import numpy as np
import pandas as pd
import neurokit2 as nk
from .DashApp import ecg_dash, rsp_dash
from .utilities.volume import get_speaker_output_volume

# Create your views here.
def index(request):
    vol = get_speaker_output_volume() # Obtain the speaker volume of system

    return render(request, 'heart.html', {
        'vol': vol
    })