from django.urls import include, path 
from .views import (
    index, services, social, economique, solution, project, 
    calcul, about, blog, event, credit, service_detail, energie, member_detail, team_list
)

urlpatterns = [
    path('', index, name='index'),
    path('social/', social, name='social'),
    path('economique/', economique, name='economique'),
    path('solution/', solution, name='solution'),
    path('project/', project, name='project'),
    path('calcul-emprunte-carbone/', calcul, name='calcul'),
    path('services/', services, name='services'),
    path('a-propos/', about, name='about'),
    path('equipe/<slug:slug>/', member_detail, name='member_detail'),
    path('equipe/', team_list, name='team_list'),
    path('blog/', blog, name='blog'),
    path('event/', event, name='event'),
    path('credit-carbone/', credit, name='credit'),
    path('services_detail/', service_detail, name='services_detail'),  # Alternative URL for better UX
    path('energie/', energie, name='energie'),
]
