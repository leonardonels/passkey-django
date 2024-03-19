from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User

class Registration(UserCreationForm):
    def save(self , commit=True):
        user = super().save(commit)
        g=Group.object.get(name="user")
        g.user_set.add(user)
        return user
    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class UsernameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']