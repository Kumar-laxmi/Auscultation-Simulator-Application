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
    hr_plus = forms.CharField(widget=forms.TextInput(attrs={
        'type': 'button',
        'class': 'btn btn-link btn-outline-danger',
        'id': 'hr_plus',
        'data-mdb-ripple-color': 'dark'
    }))
    hr_minus = forms.CharField(widget=forms.TextInput(attrs={
        'type': 'button',
        'class': 'btn btn-link btn-outline-danger',
        'id': 'hr_minus',
        'data-mdb-ripple-color': 'dark'
    }))
    card_text = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'card-text text-success',
        'style': 'transition: 0.5s;',
        'id': 'hr_show'
    }))