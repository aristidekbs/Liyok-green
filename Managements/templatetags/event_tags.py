from django import template
from django.utils import timezone
from ..models import Event # Les deux points .. signifient "dossier parent"

register = template.Library()

@register.simple_tag
def get_next_event():
    """
    Retourne le prochain événement à venir.
    """
    now = timezone.now()
    
    # On cherche l'événement
    event = Event.objects.filter(
        status='published',
        is_active=True,
        start_date__gte=now  # Doit être dans le futur
    ).order_by('start_date').first()
    
    return event