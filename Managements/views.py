from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import Service, TeamMember

# Create your views here.
def index(request):
    team = TeamMember.objects.all()
    return render(request, 'pages/index.html', context={'team': team})

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
    team = TeamMember.objects.all()
    return render(request, 'pages/about.html', context={'team': team})


def team_list(request):
    """Vue pour afficher la liste de tous les membres de l'équipe"""
    team = TeamMember.objects.all()
    return render(request, 'pages/team_list.html', context={'team': team})

def member_detail(request, slug):
    """Vue pour afficher les détails d'un membre spécifique"""
    member = get_object_or_404(TeamMember, slug=slug, )
    other_members = TeamMember.objects.exclude(slug=slug).order_by('?')[:3]

    
    context = {
        'member': member,
        'other_members': other_members,
        'title': f"{member.name} - {member.role}",
        'meta_description': member.description[:160] if member.description else f"Découvrez le profil de {member.name}, {member.role} chez Liyok Green.",
    }
    return render(request, 'pages/member_detail.html', context)

def blog(request): 
    return render(request, 'pages/blog.html')

def event(request): 
    return render(request, 'pages/event.html')

def credit(request): 
    return render(request, 'pages/credit.html')


def service_detail(request):
   

    return render(request, 'pages/service_detail.html')


def energie(request):
    return render(request, 'pages/energie.html', context={})
