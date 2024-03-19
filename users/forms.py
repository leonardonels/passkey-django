from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from .models import NormalUser

class RegistrationForm(UserCreationForm):
    username=forms.CharField(max_length=25, required=True)

    class Meta:
        model = NormalUser
        fields = ['username', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = NormalUser
        fields = ['username', 'email', 'first_name', 'last_name']

class UsernameChangeForm(forms.ModelForm):
    class Meta:
        model = NormalUser
        fields = ['username']