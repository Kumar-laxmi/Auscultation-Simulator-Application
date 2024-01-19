from django import forms
from .models import heartAudio, lungAudio, heartRate

class heartAudioForms(forms.ModelForm):
    class Meta:
        model = heartAudio
        fields = ['sound_name', 'sound_type', 'audio_file']

class lungAudioForm(forms.ModelForm):
    class Meta:
        model = lungAudio
        fields = ['sound_name', 'sound_type', 'audio_file']


class updateHeartRateForm(forms.Form):
    class Meta:
        model = heartRate
        fields = ['heartrate']