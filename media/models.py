from django.db import models
from django.contrib.auth.models import User

class image_link(models.Model):
    title = models.CharField(max_length=200)
    link = models.URLField()

    def __str__(self):
        return self.title