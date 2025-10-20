from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.template.loader import render_to_string
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Galerie, Category, Service, ServiceMedia, Event, EventRegistration, TeamMember, Testimonial, Tag, Article, MediaArticle
from .forms import EventRegistrationForm

def Home(request):
    # Récupérer les témoignages depuis la base de données
    testimonials = Testimonial.objects.all()

    # Récupérer les 4 premiers services actifs
    services = Service.objects.filter(is_active=True).order_by('order')[:4]

    context = {
        'testimonials': testimonials,
        'services': services,
        'title': 'Accueil'
    }
    return render(request, 'pages/index.html', context)

def About(request):
    # Récupérer tous les membres de l'équipe
    team_members = TeamMember.objects.all().order_by('id')
    
    # Récupérer les témoignages depuis la base de données
    testimonials = Testimonial.objects.all()
    
    # Statistiques de l'entreprise
    stats = {
        'projects_completed': 250,
        'happy_clients': 180,
        'years_experience': 10,
        'team_members': team_members.count()
    }
    
    context = {
        'team_members': team_members,
        'stats': stats,
        'testimonials': testimonials,
        'title': 'À propos de nous'
    }
    
    return render(request, 'pages/about.html', context)

def Contact(request):
    from .models import SiteSetting
    site_settings = SiteSetting.objects.first()

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Créer le message de contact
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        # Ici vous pouvez ajouter l'envoi d'email si nécessaire
        messages.success(request, 'Votre message a été envoyé avec succès !')
        return redirect('contact')

    context = {
        'site_settings': site_settings,
        'title': 'Contact'
    }
    return render(request, 'pages/contact.html', context)

def galery_categories(request):
    """
    Vue pour afficher toutes les catégories de la galerie
    """
    categories = Category.objects.filter(is_active=True, galeries__isnull=False).distinct()
    
    context = {
        'categories': categories,
        'title': 'Nos Galeries',
    }
    return render(request, 'pages/category-galery.html', context)


def galerie_detail(request, category_slug, galery_slug):
    """
    Vue pour afficher le détail d'une galerie avec ses images/vidéos
    """
    import os
    from django.conf import settings
    
    print("=== DEBUG: Début de la vue galerie_detail ===")
    print(f"Category slug: {category_slug}, Galery slug: {galery_slug}")
    
    # Vérifier que la catégorie est active et que la galerie appartient bien à cette catégorie
    try:
        galerie = Galerie.objects.get(
            slug=galery_slug,
            categorie__slug=category_slug,
            categorie__is_active=True,
            est_publie=True
        )
        print(f"Galerie trouvée: {galerie.titre}")
    except Galerie.DoesNotExist:
        print("ERREUR: Galerie non trouvée avec les paramètres fournis")
        from django.http import Http404
        raise Http404("Galerie non trouvée")
    
    # Récupérer les images de la galerie triées par ordre
    images = galerie.images.all().order_by('ordre')
    print(f"Nombre d'images trouvées: {images.count()}")
    
    # Afficher les chemins des images pour le débogage
    for img in images:
        print(f"Image: {img.image.name} - Chemin complet: {os.path.join(settings.MEDIA_ROOT, img.image.name)}")
        print(f"Image URL: {img.image.url if img.image else 'Aucune image'}")
    
    # Récupérer les autres galeries pour la section "Voir aussi"
    autres_galeries = Galerie.objects.filter(
        est_publie=True,
        categorie=galerie.categorie
    ).exclude(id=galerie.id).order_by('-date_creation')[:4]
    
    context = {
        'galerie': galerie,
        'category': galerie.categorie,  # Ajout de la catégorie au contexte
        'images': images,
        'autres_galeries': autres_galeries,
        'title': f'Galerie - {galerie.titre}',
    }
    
    # Vérifier si le répertoire media existe
    media_dir = settings.MEDIA_ROOT
    print(f"Dossier MEDIA_ROOT: {media_dir}")
    print(f"Dossier MEDIA_ROOT existe: {os.path.exists(media_dir)}")
    
    # Vérifier les permissions du dossier
    if os.path.exists(media_dir):
        print(f"Permissions du dossier: {oct(os.stat(media_dir).st_mode)[-3:]}")
    
    print("=== FIN DEBUG ===")
    return render(request, 'pages/galerie_detail.html', context)

def event_list(request):
    """Affiche la liste des événements à venir et passés"""
    upcoming_events = Event.objects.filter(
        is_active=True,
        status='published',
        start_date__gte=timezone.now()
    ).order_by('start_date')
    
    past_events = Event.objects.filter(
        is_active=True,
        status='published',
        end_date__lt=timezone.now()
    ).order_by('-start_date')
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'title': 'Nos Événements'
    }
    
    return render(request, 'pages/event.html', context)

def event_detail(request, slug):
    try:
        event = get_object_or_404(Event, slug=slug, is_active=True, status='published')

        # Vérifier si les inscriptions sont ouvertes
        registration_open = False
        if event.registration_required and event.registration_deadline:
            registration_open = timezone.now() <= event.registration_deadline

        # POST → soumission du formulaire
        if request.method == 'POST':
            form = EventRegistrationForm(request.POST)

            if not registration_open:
                return JsonResponse({
                    'success': False,
                    'message': 'Les inscriptions pour cet événement sont actuellement fermées.',
                    'error_type': 'RegistrationClosed'
                }, status=400)

            if form.is_valid():
                try:
                    # Créer l'instance avec commit=False pour modifier les champs avant sauvegarde
                    registration = form.save(commit=False)
                    
                    # S'assurer que l'événement est correctement défini
                    registration.event = event
                    
                    # Valider le modèle
                    registration.full_clean()
                    
                    # Sauvegarder l'inscription
                    registration.save()
                    
                    # Sauvegarder les relations many-to-many si nécessaire
                    form.save_m2m()
                    
                except ValidationError as e:
                    # Journaliser l'erreur pour le débogage
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Erreur de validation lors de l'inscription: {e}")
                    
                    return JsonResponse({
                        'success': False,
                        'message': 'Erreur de validation du formulaire.',
                        'errors': e.message_dict if hasattr(e, 'message_dict') else str(e)
                    }, status=400)

                # Réponse AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Votre inscription a bien été enregistrée !',
                        'html': render_to_string('includes/registration_success.html')
                    })

                # Réponse standard
                messages.success(request, 'Votre inscription a bien été enregistrée !')
                return redirect('event-detail', slug=event.slug)

            else:
                # Formulaire invalide
                errors_html = render_to_string('includes/registration_form.html', {'form': form, 'event': event}, request=request)
                return JsonResponse({
                    'success': False,
                    'message': 'Veuillez corriger les erreurs ci-dessous.',
                    'errors': form.errors,
                    'html': errors_html
                }, status=400)

        # GET → formulaire vide
        else:
            form = EventRegistrationForm()

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f"Une erreur est survenue: {str(e)}",
            'error_type': type(e).__name__
        }, status=500)

    context = {
        'event': event,
        'form': form,
        'registration_open': registration_open,
        'title': event.title,
        'now': timezone.now()
    }

    # GET AJAX → retourner uniquement le formulaire
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'html': render_to_string('includes/registration_form.html', context, request=request)
        })

    return render(request, 'pages/event_detail.html', context)


def service_list(request):
    """Vue pour afficher la liste des services actifs"""
    services = Service.objects.filter(is_active=True).order_by('order', 'title')
    context = {
        'services': services,
        'title': 'Nos Services'
    }
    return render(request, 'pages/service.html', context)

def service_detail(request, slug=None):
    """Vue pour afficher le détail d'un service"""
    if not slug:
        from django.http import Http404
        raise Http404("Service non spécifié")
    
    try:
        service = Service.objects.get(slug=slug, is_active=True)
    except Service.DoesNotExist:
        from django.http import Http404
        raise Http404("Service non trouvé")
    
    # Récupérer les autres services pour la section "Autres services"
    other_services = Service.objects.filter(is_active=True).exclude(id=service.id).order_by('order', 'title')[:3]
    
    context = {
        'service': service,
        'other_services': other_services,
        'title': service.title
    }
    return render(request, 'pages/service_detail.html', context)


def article_list(request, category_slug=None):
    """
    Vue pour afficher la liste des articles, avec filtrage par catégorie si nécessaire
    """
    # Récupérer la catégorie si un slug est fourni
    category = None
    articles = Article.objects.filter(is_published=True).order_by('-published_at')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        articles = articles.filter(category=category)

    # Pagination
    paginator = Paginator(articles, 9)  # 9 articles par page
    page_number = request.GET.get('page')
    try:
        articles = paginator.page(page_number)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    # Récupérer les derniers articles pour la sidebar
    recent_articles = Article.objects.filter(
        is_published=True
    ).exclude(id__in=[a.id for a in articles if hasattr(a, 'id')]).order_by('-published_at')[:5]

    # Récupérer toutes les catégories avec le nombre d'articles
    categories = Category.objects.annotate(
        article_count=models.Count('articles', filter=models.Q(articles__is_published=True))
    ).filter(article_count__gt=0)

    # Récupérer tous les tags avec le nombre d'articles
    all_tags = Tag.objects.annotate(
        num_articles=models.Count('articles', filter=models.Q(articles__is_published=True))
    ).filter(num_articles__gt=0)

    context = {
        'title': 'Articles' if not category else f'Articles - {category.name}',
        'SITE_NAME': 'Liyok Web',
        'articles': articles,
        'category': category,
        'categories': categories,
        'recent_articles': recent_articles,
        'all_tags': all_tags,
        'total_articles': articles.paginator.count if hasattr(articles, 'paginator') else articles.count()
    }

    return render(request, 'pages/article_list.html', context)


def article_detail(request, slug):
    """
    Vue pour afficher le détail d'un article
    """
    # Récupérer l'article avec son slug
    article = get_object_or_404(
        Article.objects.prefetch_related('media_article', 'tags'),
        slug=slug,
        is_published=True
    )

    # Incrémenter le compteur de vues
    article.views = models.F('views') + 1
    article.save(update_fields=['views'])
    article.refresh_from_db()

    # Récupérer les articles récents (exclure l'article actuel)
    recent_articles = Article.objects.filter(
        is_published=True
    ).exclude(id=article.id).order_by('-published_at')[:5]

    # Récupérer les catégories avec le nombre d'articles
    categories = Category.objects.annotate(
        article_count=models.Count('articles', filter=models.Q(articles__is_published=True))
    ).filter(article_count__gt=0)

    # Récupérer tous les tags
    all_tags = article.tags.all()

    # Récupérer les articles similaires (même catégorie)
    related_articles = Article.objects.filter(
        category=article.category,
        is_published=True
    ).exclude(id=article.id).order_by('-published_at')[:3]

    context = {
        'article': article,
        'recent_articles': recent_articles,
        'categories': categories,
        'all_tags': all_tags,
        'related_articles': related_articles,
        'title': article.title,
        'SITE_NAME': 'Liyok Web',
    }

    return render(request, 'pages/article_detail.html', context)


def article_list_old(request):
    return render(request, 'pages/article_list.html')


def article_detail_old(request):
    return render(request, 'pages/article_detail.html')






