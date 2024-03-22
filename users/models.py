from django.db import models
from django.contrib.auth.models import AbstractUser
from cryptography.fernet import Fernet
from django.utils.encoding import force_bytes
from mysite.settings import SECRET_KEY
import pyotp,base64

# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN="ADMIN", 'admin'
        USER="USER", 'user'
        VERIFIED="VERIFIED", 'verified'

    base_role=Role.ADMIN

    role=models.CharField(max_length=50,choices=Role.choices)
    otp = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=200, blank=True)

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
        otp_secret=pyotp.random_base32()
        fernet_otp_secret=self.encrypt_otp_secret(otp_secret)
        self.otp_secret=fernet_otp_secret.decode('utf-8')
        self.save()

    def encrypt_otp_secret(self, otp_secret):
        key=force_bytes(SECRET_KEY)[:32]
        fernet=Fernet(base64.b64encode(key))
        token=fernet.encrypt(otp_secret.encode('utf-8'))
        return token

    def decrypt_otp_secret(self, token):
        key=force_bytes(SECRET_KEY)[:32]
        fernet=Fernet(base64.b64encode(key))
        otp_secret=fernet.decrypt(token.encode('utf-8')).decode('utf-8')
        return otp_secret
        
class NormalUser(User):

    base_role=User.Role.USER

    class Meta:
        proxy=True