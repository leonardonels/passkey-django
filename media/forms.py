from django import forms
from .models import image_link

class ImageForm(forms.ModelForm):
    class Meta:
        model = image_link
        fields = ['title', 'link']