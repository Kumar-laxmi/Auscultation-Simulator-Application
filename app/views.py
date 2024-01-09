from urllib import request
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext

import plotly.graph_objects as go
from plotly.offline import plot
import wave, sys
import numpy as np
import pandas as pd
import neurokit2 as nk
from .DashApp import ecg_dash, rsp_dash

# Create your views here.
def index(request):
    return render(request, 'index.html', {})