from django.db import models
from users.models import User

# Create your models here.

class Credential(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credentials')
    credential_id = models.BinaryField()
    public_key = models.BinaryField()
    sign_counts = models.IntegerField()
    transports = models.CharField(max_length=255)