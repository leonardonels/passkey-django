from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from media.models import image_link
from users.forms import RegistrationForm
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView

def home(request):
    images = image_link.objects.all()
    return render(request, 'home.html', {'images': images})

def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log in the user
            login(request, user)
            return redirect('home')  # Redirect to the home page after signup
    else:
        form = RegistrationForm()
    return render(request, 'signup.html', {'form': form})