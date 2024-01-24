from django import forms
from .models import heartAudio, lungAudio, heartRate, heartSound

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

class heartSoundForm(forms.Form):
    class Meta:
        model = heartSound
        fields = []