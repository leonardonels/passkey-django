from django.urls import path
from .views import *

app_name = "media"

urlpatterns = [

    path('create', create, name='create'),
]
