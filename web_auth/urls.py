from django.urls import path
from .views import *

urlpatterns = [
    path('registration/', registration, name='registration'),
    path('registration_verification/', registration_verification, name='registration_verification'),
]
