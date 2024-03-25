from django.urls import path
from .views import *

app_name = "web_auth"

urlpatterns = [
    path('registration/', registration, name='registration'),
    path('registration_verification/', registration_verification, name='registration_verification'),
    path('authentication/', authentication, name='authentication'),
    path('authentication_verification/', authentication_verification, name='authentication_verification'),
    path('remove_passkey/', remove_passkey, name='remove_passkey'),
    path('login_with_passkey/', login_with_passkey, name='login_with_passkey'),
    path('login_with_passkey/set_username/', set_username_in_session, name='set_username'),
]
