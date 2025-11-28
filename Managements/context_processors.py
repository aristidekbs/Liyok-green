from .models import SiteSetting, Event, timezone

def site_settings(request):
    try:
        site_setting = SiteSetting.objects.first()
    except SiteSetting.DoesNotExist:
        site_setting = None
    return {'site_setting': site_setting}

def global_next_event(request):
    now = timezone.now()
    
    # On cherche l'événement
    next_event = Event.objects.filter(
        status='published',
        is_active=True,
        start_date__gte=now
    ).order_by('start_date').first()

    # --- DEBUG : AJOUTE CES LIGNES ---
    print(f"--- DEBUG CONTEXT PROCESSOR ---")
    print(f"Heure actuelle serveur : {now}")
    print(f"Événement trouvé : {next_event}")
    if not next_event:
        print("Aucun événement futur et publié trouvé.")
        # Test pour voir s'il y en a au moins un en base sans le filtre de date
        count = Event.objects.count()
        print(f"Total événements en base : {count}")
    # ---------------------------------

    return {'top_bar_event': next_event}