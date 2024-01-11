from django import forms
from .models import heartAudio, lungAudio

class heartAudioForms(forms.ModelForm):
    class Meta:
        model = heartAudio
        fields = ['sound_name', 'sound_type', 'audio_file']

class lungAudioForm(forms.ModelForm):
    class Meta:
        model = lungAudio
        fields = ['sound_name', 'sound_type', 'audio_file']