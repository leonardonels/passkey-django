from django.urls import path
from .views import *

app_name = "users"

urlpatterns = [

    path('profile/', profile, name='profile'),
    path('profile/delete/', delete_account, name='delete_profile'),
    path('profile/change_username/', change_username, name='change_username'),
    path('profile/change_password/', change_password, name='change_password'),
    path('profile/toggle_otp/', toggle_otp, name='toggle_otp'),
    path('profile/setup_otp/', setup_otp, name='setup_otp')
]
