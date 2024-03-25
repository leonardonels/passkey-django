from django.urls import path
from .views import *

app_name = "web_auth"

urlpatterns = [
    path('registration/', registration, name='registration'),
    path('registration_verification/', registration_verification, name='registration_verification'),
    path('remove_passkey/', remove_passkey, name='remove_passkey'),
]
