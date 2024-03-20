from django.db import models
from django.contrib.auth.models import AbstractUser
import pyotp

# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN="ADMIN", 'admin'
        USER="USER", 'user'
        VERIFIED="VERIFIED", 'verified'

    base_role=Role.ADMIN

    role=models.CharField(max_length=50,choices=Role.choices)
    otp = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=32, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role=self.base_role
        return super().save(*args, **kwargs)
    
    def is_superuser_custom(self):
        return self.role == 'ADMIN'
    
    @property
    def is_admin(self):
        return self.is_superuser_custom()
    
    def add_otp(self):
        self.otp = True
    
    def remove_otp(self):
        self.otp = False

    def toggle_otp(self):
        if self.otp:
            self.remove_otp()
        else:
            self.add_otp()
        self.save()

    def set_secret(self):
        self.otp_secret=pyotp.random_base32()
        self.save()
        
class NormalUser(User):

    base_role=User.Role.USER

    class Meta:
        proxy=True