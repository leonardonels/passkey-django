from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .models import image_link
from .forms import *

@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            # Associate the current user with the uploaded image
            img = form.save(commit=False)
            img.user = request.user
            img.save()
            return redirect('home')  # Redirect to home or wherever appropriate
    else:
        form = ImageForm()
    return render(request, 'upload_image.html', {'form': form})

def search(request):
    query = request.GET.get('q', '')  # Get the search query from request parameters
    if query:
        images = image_link.objects.filter(title__icontains=query)  # Filter images by name containing the query
    else:
        images = image_link.objects.all()  # Retrieve all images if search query is empty
    return render(request, 'search.html', {'images': images, 'query': query})

def portfolio(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Fetch all images uploaded by the current user
        images = image_link.objects.filter(user=request.user)
        return render(request, 'portfolio.html', {'images': images})
    else:
        # Redirect to login page if the user is not authenticated
        return redirect('login')
    
@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            return redirect('/media/profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

@login_required
def change_username(request):
    if request.method == 'POST':
        form = UsernameChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/media/profile')
    else:
        form = UsernameChangeForm(instance=request.user, data={'username': request.user.username})
    return render(request, 'change_username.html', {'form': form})

def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if request.user.check_password(password):
            request.user.delete()
            return redirect('home')
    return render(request, 'delete.html')