from django.core.files.storage import FileSystemStorage
from django.db import models

from .dependencies import dir_name

class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return name

class heartAudio(models.Model):
    SOUND_NAME_CHOICES = dir_name.sound_name_choices_heart
    SOUND_TYPE_CHOICES = dir_name.sound_type_choices_heart
    sound_name = models.CharField(max_length=50, choices=SOUND_NAME_CHOICES)
    sound_type = models.CharField(max_length=1, choices=SOUND_TYPE_CHOICES)
    audio_file = models.FileField(
        # upload_to=lambda instance, filename: 'heart/{}/{}/{}'.format(getattr(instance, 'sound_name'), getattr(instance, 'sound_type'), filename),
        storage=OverwriteStorage()
    )

    def __str__(self):
        return f"heart_{self.sound_name}_{self.sound_type}"
    
class lungAudio(models.Model):
    SOUND_NAME_CHOICES = dir_name.sound_name_choices_lung
    SOUND_TYPE_CHOICES = dir_name.sound_type_choices_lung
    sound_name = models.CharField(max_length=50, choices=SOUND_NAME_CHOICES)
    sound_type = models.CharField(max_length=3, choices=SOUND_TYPE_CHOICES)
    audio_file = models.FileField(
        # upload_to=lambda instance, filename: 'lungs/{}/{}/{}'.format(getattr(instance, 'sound_name'), getattr(instance, 'sound_type'), filename),
        storage=OverwriteStorage()
    )

    def __str__(self):
        return f"lungs_{self.sound_name}_{self.sound_type}"
    
class heartRate(models.Model):
    heartrate = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.heartrate}"
    
class heartSound(models.Model):
    def __str__(self):
        return "Button Clicked"