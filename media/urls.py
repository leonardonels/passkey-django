from django.urls import path
from .views import *

app_name = "media"

urlpatterns = [

    path('upload', upload_image, name='upload'),
    path('search', search, name='search'),
    path('portfolio', portfolio, name='portfolio'),
    path('portfolio/edit/<int:image_id>/', edit_image, name='edit_image'),
    path('portfolio/edit/delete/<int:image_id>/', delete_image, name='delete_image'),
]
