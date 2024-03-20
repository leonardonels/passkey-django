from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from media.models import image_link
from users.forms import RegistrationForm
from django.contrib.auth import login, logout, authenticate
from .utils import send_otp
from datetime import datetime
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
            #send one time password
            #...
            send_otp(request)
            request.session['username']=username
            return redirect('otp')
            
            #login(request, user)
            #return redirect('home')
        else:
            error_message = 'invalid username or password'
    return render(request, 'login.html', {'error_message':error_message})

def otp(request):
    error_message=None
    if request.method == 'POST':
        otp = request.POST['otp']
        username = request.session['username'] 

        otp_secret_key = request.session['otp_secret_key']
        otp_valid_date = request.session['otp_valid_date']

        if otp_secret_key and otp_valid_date is not None:
            valid_date=datetime.fromisoformat(otp_valid_date)

            if valid_date > datetime.now():
                 totp = pyotp.TOTP(otp_secret_key, interval=60)

                 if totp.verify(otp):
                    user=get_object_or_404(User, username=username)
                    login(request, user)

                    del request.session['otp_secret_key']
                    del request.session['otp_valid_date']

                    return redirect('home')
                 else:
                     error_message="invalid one time password"
            else:
                error_message="one time password has expired"
        else:
            error_message="ops...something went wrong :("
     
    return render(request, 'otp.html', {'error_message':error_message})