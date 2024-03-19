from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
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

def edit_image(request, image_id):
    image = get_object_or_404(image_link, id=image_id)
    if request.method == 'POST':
        form = ImageForm(request.POST, instance=image)
        if form.is_valid():
            form.save()
            return redirect('/media/portfolio')
    else:
        form = ImageForm(instance=image)
    return render(request, 'edit.html', {'form': form, 'image': image})

def delete_image(request, image_id):
    image = get_object_or_404(image_link, id=image_id)
    if request.method == 'POST':
        image.delete()
        return redirect('/media/portfolio')
    return render(request, 'delete_image.html', {'image': image})
