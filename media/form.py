from django import forms
from .models import image_link
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

class ImageForm(forms.ModelForm):
    class Meta:
        model = image_link
        fields = ['title', 'link']

class Registration(UserCreationForm):
    def save(self , commit=True):
        user = super().save(commit)
        g=Group.object.get(name="user")
        g.user_set.add(user)
        return user