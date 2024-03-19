from django.urls import path
from .views import *

app_name = "users"

urlpatterns = [

    path('profile/', profile, name='profile'),
    path('profile/delete/', delete_account, name='delete_profile'),
    path('profile/change_username/', change_username, name='change_username'),
    path('profile/change_password/', change_password, name='change_password'),
]
