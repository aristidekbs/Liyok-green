from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import Service

# Create your views here.
def index(request):
    return render(request, 'pages/index.html', context={})

def social(request):
    return render(request, 'pages/social.html', context={})

def economique(request):
    return render(request, 'pages/economique.html', context={})

def solution(request):
    return render(request, 'pages/solution.html', context={})

def project(request):
    return render(request, 'pages/project.html')

def calcul(request):
    return render(request, 'pages/calcul.html')



def services(request):
    
    return render(request, 'pages/service.html')

def about(request):
    return render(request, 'pages/about.html')

def blog(request): 
    return render(request, 'pages/blog.html')

def event(request): 
    return render(request, 'pages/event.html')

def credit(request): 
    return render(request, 'pages/credit.html')

from django.shortcuts import render, get_object_or_404
from .models import Service

def service_detail(request):
   

    return render(request, 'pages/service_detail.html')


def energie(request):
    return render(request, 'pages/energie.html', context={})
