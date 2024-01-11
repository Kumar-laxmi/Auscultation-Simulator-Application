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
        upload_to='app/static/audio/heart/{}/{}/'.format(sound_name, sound_type),
        storage=OverwriteStorage()
    )

    def __str__(self):
        return f"heart_{self.sound_name}_{self.sound_type}"
