from django.db import models
from embed_video.fields import EmbedVideoField

# Create your models here.
class Video(models.Model):
    title = models.CharField(max_length=100)
    url = EmbedVideoField()
    added = models.DateTimeField(auto_now_add=True)