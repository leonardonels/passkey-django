from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from io import BytesIO
from .forms import *
from .models import User
import pyotp, base64, qrcode
from web_auth.models import Credential

# Create your views here.

@login_required
def profile(request):
    user = request.user
    passkey_exists = Credential.objects.filter(user_id=user.id).exists()
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'profile.html', {'form': form, 'passkey_exists': passkey_exists})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            return redirect('/users/profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

@login_required
def change_username(request):
    if request.method == 'POST':
        form = UsernameChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/users/profile')
    else:
        form = UsernameChangeForm(instance=request.user, data={'username': request.user.username})
    return render(request, 'change_username.html', {'form': form, 'username': request.user.username})

@login_required
def delete_account(request):
    message=""
    if request.method == 'POST':
        password = request.POST.get('password')
        if request.user.check_password(password):
            request.user.delete()
            return redirect('home')
        else:
            message="Invalid password. Please try again."
    context={'message':message}
    return render(request, 'delete.html', context)

@login_required
def toggle_otp(request):
    if request.method == 'POST':
        user = request.user
        if user:
            user.toggle_otp()
    return redirect('/users/profile')

@login_required
def setup_otp(request):
    user = request.user
    if request.method == 'POST':
        if user:
            user.set_secret()
            user.generate_backup_codes()
            user.toggle_otp()

            # QR code
            totp = pyotp.TOTP(user.decrypt_otp_secret(user.otp_secret))
            otp_uri = totp.provisioning_uri(user.username, issuer_name="Django RAW")
            qr = qrcode.make(otp_uri)
            
            # save QR in a buffer
            buffer = BytesIO()
            qr.save(buffer)
            
            # base64 base64 encoding of QR image
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return render(request, 'setup_otp.html', {'qr_base64': qr_base64, 
                                                      'otp_secret': user.decrypt_otp_secret(user.otp_secret), 
                                                      'backup_codes': user.decrypt_backup_codes(user.backup_codes)
                                                     })
        else:
            print("non user")
    else:
        print("non post")
    return render(request, 'setup_otp.html')
