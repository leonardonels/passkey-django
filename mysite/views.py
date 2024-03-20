from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from media.models import image_link
from users.forms import RegistrationForm
from django.contrib.auth import login, logout, authenticate
from datetime import datetime, timedelta
from users.models import User 
import pyotp

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
            if user.otp:
                #send_otp(request)
                request.session['username']=username
                return redirect('otp')
            else:
                login(request, user)
                return redirect('home')
        else:
            error_message = 'invalid username or password'
    return render(request, 'login.html', {'error_message':error_message})

def logout_view(request):
    logout(request)
    return redirect('home')

def otp(request):
        error_message=None
        username = request.session['username']
        user=get_object_or_404(User, username=username)
        secret=user.otp_secret
        totp=pyotp.TOTP(secret)
        print("Current OTP:", totp.now())

        if request.method == 'POST':
            otp=request.POST['otp']
            print(otp)
            if totp.verify(otp):
                login(request, user)
                return redirect('home')
            else:
                error_message="invalid one time password"
        return render(request, 'otp.html', {'error_message':error_message})