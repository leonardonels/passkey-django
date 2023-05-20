from django.shortcuts import render
from django.urls import reverse_lazy

def home(request):
    return render(request, template_name="home.html")