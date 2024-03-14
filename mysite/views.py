from django.shortcuts import render
from django.urls import reverse_lazy
from media.models import image_link
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView

def home(request):
    images = image_link.objects.all()
    return render(request, 'home.html', {'images': images})

class UserCreateView(CreateView):
    form_class=UserCreationForm
    template_name="user_create.html"
    succesfull_urls=reverse_lazy("login")