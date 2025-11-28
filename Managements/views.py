from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import  TeamMember , Service, Event
from django.contrib import messages
from django.utils import timezone

# Create your views here.
def index(request):
    team = TeamMember.objects.all()
    services = Service.objects.all()
    events = Event.objects.all()
    return render(request, 'pages/index.html', context={'team': team, 'services': services, 'events': events})

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
    services = Service.objects.all()
    return render(request, 'pages/service.html', context={'services': services})


def service_detail(request, slug):
    service = Service.objects.get(slug=slug)
    return render(request, 'pages/service_detail.html', context={'service': service})

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
    events = Event.objects.filter(status='published', is_active=True).order_by('start_date')
    return render(request, 'pages/event.html', context={'events': events})

def credit(request): 
    return render(request, 'pages/credit.html')



def energie(request):
    return render(request, 'pages/energie.html', context={})

def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug)
    
    # Gestion du formulaire d'inscription (POST)
    if request.method == "POST":
        try:
            # Récupération des données
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            company = request.POST.get('company')
            
            # Création de l'inscription
            # Note: La méthode .clean() du modèle sera appelée lors du save() ou manuellement
            registration = EventRegistration(
                event=event,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                company=company
            )
            # On vérifie la validation (places dispo, dates...)
            registration.full_clean() 
            registration.save()

            messages.success(request, f"Merci {first_name}, votre inscription est confirmée !")
            return redirect('event_detail', slug=slug)

        except Exception as e:
            # Si une erreur (ex: plus de places, email déjà utilisé)
            messages.error(request, f"Erreur lors de l'inscription : {e}")

    return render(request, 'pages/event_detail.html', {'event': event})
