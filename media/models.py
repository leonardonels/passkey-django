from django.db import models
from users.models import User

class image_link(models.Model):
    title = models.CharField(max_length=25)
    link = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="images")

    def __str__(self):
        return self.title
