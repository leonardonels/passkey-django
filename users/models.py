from django.db import models
from django.contrib.auth.models import AbstractUser
from cryptography.fernet import Fernet
from django.utils.encoding import force_bytes
from mysite.settings import SECRET_KEY
import pyotp,base64, random

# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN="ADMIN", 'admin'
        USER="USER", 'user'
        VERIFIED="VERIFIED", 'verified'

    base_role=Role.ADMIN
    base_backend='django.contrib.auth.backends.ModelBackend'

    role=models.CharField(max_length=50,choices=Role.choices)
    otp = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=200, blank=True)
    backup_codes = models.CharField(max_length=200, blank=True)
    backend = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role=self.base_role
        if not self.backend:
            self.backend=self.base_backend
        return super().save(*args, **kwargs)
    
    def set_custom_backend(self):
        self.backend='web_auth.auth.CustomAuthBackend'
        self.save()
    
    def reset_backend(self):
        self.backend=self.base_backend
        self.save()
    
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
    
    def generate_backup_codes(self):
        backup_codes = []
        for _ in range(10):
            backup_code = ''.join(random.choices('0123456789', k=6))
            backup_codes.append(backup_code)
        print(backup_codes)
        self.encrypt_backup_codes(backup_codes)

    def encrypt_backup_codes(self, backup_codes):
        key=force_bytes(SECRET_KEY)[:32]
        fernet=Fernet(base64.b64encode(key))
        token=fernet.encrypt(','.join(backup_codes).encode('utf-8')).decode('utf-8')
        print(token)
        self.backup_codes=token
        self.save()

    def decrypt_backup_codes(self, token):
        key=force_bytes(SECRET_KEY)[:32]
        fernet=Fernet(base64.b64encode(key))
        token=token.encode('utf-8')
        decrypted_codes = fernet.decrypt(token).decode().split(',')
        print(decrypted_codes)
        return decrypted_codes
            
class NormalUser(User):

    base_role=User.Role.USER

    class Meta:
        proxy=True