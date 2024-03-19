from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from media.models import image_link
from users.forms import RegistrationForm
from django.contrib.auth import login, logout, authenticate

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

def login_view(request):
    error_message=None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            #send one time password
            #...
            login(request, user)
            #return redirect('otp')
            return redirect('home')
        else:
            error_message = 'invalid username or password'
    return render(request, 'login.html', {'error_message':error_message})

#def otp(request):
#    return render(request, 'otp.html', {})