"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from app.views import *
from app.DashApp.hbr_dash import graphChange

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('heartUpdate/', heartUpdate),
    path('breathUpdate/', breathUpdate),
    path('soundPlay/', soundPlay),
    path('mitralVolumeChange/', mitralVolumeChange),
    path('aorticVolumeChange/', aorticVolumeChange),
    path('pulmonaryVolumeChange/', pulmonaryVolumeChange),
    path('tricuspidVolumeChange/', tricuspidVolumeChange),
    path('erbVolumeChange/', erbVolumeChange),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('graphChange/', graphChange),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
