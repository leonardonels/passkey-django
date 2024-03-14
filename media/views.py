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
def delete_account(request):
    if request.method == 'POST':
        # Delete the user account
        request.user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')  # Redirect to home page or any other appropriate page
    else:
        return render(request, 'delete.html')
    
@login_required
def change_username(request):
    if request.method == 'POST':
        new_username = request.POST.get('new_username')
        request.user.username = new_username
        request.user.save()
        return redirect('/media/profile')  # Redirect to profile page after changing username
    return render(request, 'profile.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            new_password = form.cleaned_data['new_password1']
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Keep the user logged in after changing the password
            return redirect('/media/profile')  # Redirect to profile page after changing password
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'profile.html', {'form': form})