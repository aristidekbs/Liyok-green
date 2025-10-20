from .models import SiteSetting

def site_settings(request):
    try:
        settings = SiteSetting.objects.first()
    except SiteSetting.DoesNotExist:
        settings = None
    return {'site_setting': settings}


# {% if site_settings.logo %}
#     <a href="/"><img src="{{ site_settings.logo.url }}" alt="{{ site_settings.site_name }}"></a>
# {% else %}
#     <h1>{{ site_settings.site_name }}</h1>
# {% endif %}