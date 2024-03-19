from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN="ADMIN", 'admin'
        USER="USER", 'user'
        VERIFIED="VERIFIED", 'verified'

    base_role=Role.ADMIN

    role=models.CharField(max_length=50,choices=Role.choices)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role=self.base_role
        return super().save(*args, **kwargs)
    
    def is_superuser_custom(self):
        return self.role == 'ADMIN'
    
    @property
    def is_admin(self):
        return self.is_superuser_custom()
        
class NormalUser(User):

    base_role=User.Role.USER

    class Meta:
        proxy=True