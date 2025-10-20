from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class SiteSetting(models.Model):
    site_name = models.CharField(max_length=150, default="Liyok Green")
    logo = models.ImageField(upload_to="logos/")
    favicon = models.ImageField(upload_to="logos/", blank=True, null=True)
    footer_text = models.TextField(blank=True, null=True)
    email_contact = models.EmailField(blank=True, null=True)
    phone_contact = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.site_name
    

class Banner(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='banners/')
    button_text = models.CharField(max_length=100, blank=True, null=True)
    button_link = models.URLField(blank=True, null=True)
    description = models.TextField(blank = False, null = False , max_length = 300)

    def __str__(self):
        return self.title
    

class Testimonial(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    message = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.role}"


class TeamMember(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='team/')
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    description = models.TextField(blank = True , null = True)
    portofolio = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message de {self.name}"
    

class Event(models.Model):
    EVENT_STATUS = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('cancelled', 'Annulé'),
        ('completed', 'Terminé'),
    ]

    title = models.CharField(max_length=255, verbose_name='Titre')
    slug = models.SlugField(max_length=300, unique=True, blank=True, verbose_name='Slug')
    short_description = models.TextField(
        verbose_name='Description courte',
        help_text='Courte description pour les aperçus',
        default='Description à compléter',
        blank=True
    )
    description = models.TextField(verbose_name='Description complète', blank=True)
    start_date = models.DateTimeField(verbose_name='Date et heure de début')
    end_date = models.DateTimeField(verbose_name='Date et heure de fin', blank=True, null=True)
    location = models.CharField(max_length=255, verbose_name='Lieu')
    address = models.TextField(verbose_name='Adresse complète', blank=True, null=True)
    max_participants = models.PositiveIntegerField(verbose_name='Nombre maximum de participants', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Prix')
    is_free = models.BooleanField(default=True, verbose_name='Gratuit')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    status = models.CharField(max_length=20, choices=EVENT_STATUS, default='draft', verbose_name='Statut')
    registration_required = models.BooleanField(default=False, verbose_name='Inscription requise')
    registration_deadline = models.DateTimeField(verbose_name='Date limite d\'inscription', blank=True, null=True)
    created_at = models.DateTimeField(null=True, blank=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Dernière mise à jour')

    class Meta:
        verbose_name = 'Événement'
        verbose_name_plural = 'Événements'
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.start_date.strftime('%Y-%m-%d')}")
        
        # Si l'événement est gratuit, on s'assure que le prix est à 0
        if self.is_free:
            self.price = 0
            
        super().save(*args, **kwargs)

    @property
    def is_upcoming(self):
        """Vérifie si l'événement est à venir"""
        return self.start_date > timezone.now()
    
    @property
    def is_ongoing(self):
        """Vérifie si l'événement est en cours"""
        now = timezone.now()
        if self.end_date:
            return self.start_date <= now <= self.end_date
        return self.start_date.date() == now.date()
    
    @property
    def is_past(self):
        """Vérifie si l'événement est passé"""
        if self.end_date:
            return self.end_date < timezone.now()
        return self.start_date < timezone.now()
    
    @property
    def registration_open(self):
        """Vérifie si les inscriptions sont ouvertes"""
        if not self.registration_required or not self.registration_deadline:
            return False
        return timezone.now() <= self.registration_deadline and self.status == 'published'

class EventMedia(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Vidéo'),
        ('youtube', 'YouTube'),
        ('vimeo', 'Vimeo'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='image', verbose_name='Type de média')
    image = models.ImageField(upload_to='events/media/%Y/%m/', blank=True, null=True, verbose_name='Image')
    video = models.FileField(upload_to='events/videos/%Y/%m/', blank=True, null=True, verbose_name='Vidéo')
    video_url = models.URLField(blank=True, null=True, verbose_name='URL de la vidéo (YouTube/Vimeo)')
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name='Légende')
    is_featured = models.BooleanField(default=False, verbose_name='Mise en avant')
    order = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Date de création')

    class Meta:
        verbose_name = 'Média d\'événement'
        verbose_name_plural = 'Médias d\'événements'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.get_media_type_display()} - {self.event.title}"
    
    def clean(self):
        """Validation pour s'assurer qu'un seul type de média est fourni"""
        media_count = sum([
            bool(self.image),
            bool(self.video),
            bool(self.video_url)
        ])
        
        if media_count > 1:
            raise ValidationError('Vous ne pouvez sélectionner qu\'un seul type de média à la fois.')
        
        if self.media_type == 'youtube' and not self.video_url:
            raise ValidationError('Une URL YouTube est requise pour ce type de média.')
        elif self.media_type == 'vimeo' and not self.video_url:
            raise ValidationError('Une URL Vimeo est requise pour ce type de média.')
        elif self.media_type == 'video' and not self.video:
            raise ValidationError('Un fichier vidéo est requis pour ce type de média.')
        elif self.media_type == 'image' and not self.image:
            raise ValidationError('Une image est requise pour ce type de média.')


class EventRegistration(models.Model):
    """Modèle pour gérer les inscriptions aux événements"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmé'),
        ('cancelled', 'Annulé'),
        ('waiting', 'Liste d\'attente'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations', verbose_name='Événement')
    first_name = models.CharField(max_length=100, verbose_name='Prénom')
    last_name = models.CharField(max_length=100, verbose_name='Nom')
    email = models.EmailField(verbose_name='Adresse email')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Téléphone')
    company = models.CharField(max_length=200, blank=True, null=True, verbose_name='Entreprise')
    position = models.CharField(max_length=200, blank=True, null=True, verbose_name='Poste')
    number_of_people = models.PositiveIntegerField(default=1, verbose_name='Nombre de personnes')
    special_requirements = models.TextField(blank=True, null=True, verbose_name='Besoins spécifiques')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Statut')
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    confirmation_sent = models.BooleanField(default=False, verbose_name='Email de confirmation envoyé')
    notes = models.TextField(blank=True, null=True, verbose_name='Notes internes')

    class Meta:
        verbose_name = 'Inscription à un événement'
        verbose_name_plural = 'Inscriptions aux événements'
        ordering = ['-registration_date']
        unique_together = ('event', 'email')

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.event.title}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def clean(self):
        """Validation personnalisée pour les inscriptions"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Si l'événement n'est pas encore défini, on ne valide rien pour éviter l'erreur
        if not self.event_id:
            logger.warning("Aucun événement défini pour cette inscription")
            return

        # On récupère l'événement une seule fois
        event = self.event
        logger.debug(f"Validation de l'inscription pour l'événement {event.id}")

        # Vérifier si l'événement a un nombre maximum de participants
        if event.max_participants is not None:
            confirmed_count = event.registrations.exclude(id=self.id).filter(status='confirmed').count()
            logger.debug(f"Nombre de participants confirmés: {confirmed_count}/{event.max_participants}")
            
            if self.status == 'confirmed' and confirmed_count >= event.max_participants:
                error_msg = "Désolé, cet événement est complet."
                logger.warning(error_msg)
                raise ValidationError(error_msg)

        # Vérifier si les inscriptions sont ouvertes
        if event.registration_required:
            # On considère la date limite comme la "fenêtre" d'inscription
            if hasattr(event, 'registration_deadline') and event.registration_deadline:
                from django.utils import timezone
                now = timezone.now()
                logger.debug(f"Vérification de la date limite: {now} > {event.registration_deadline} = {now > event.registration_deadline}")
                
                if now > event.registration_deadline:
                    error_msg = "Les inscriptions pour cet événement sont fermées."
                    logger.warning(error_msg)
                    raise ValidationError(error_msg)
    
    def save(self, *args, **kwargs):
        # Si le statut est confirmé et que le nombre maximum de participants est atteint
        if self.status == 'confirmed' and self.event.max_participants is not None:
            confirmed_count = self.event.registrations.filter(status='confirmed').count()
            if confirmed_count >= self.event.max_participants:
                self.status = 'waiting'  # Mettre en liste d'attente
        
        super().save(*args, **kwargs)

class Testimonial(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    message = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.role}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message de {self.name}"
    
class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
    
class ProjectMedia(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='media')
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    video = models.FileField(upload_to='events/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)

    def __str__(self): 
        return f"Media for {self.project.title}"




class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name




class Galerie(models.Model):
    """
    Modèle pour gérer les galeries d'images
    """
    TYPE_CHOICES = [
        ('photo', 'Photo'),
        ('video', 'Vidéo'),
        ('mixte', 'Mixte'),
    ]
    
    titre = models.CharField(max_length=200, verbose_name='Titre de la galerie')
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name='Slug')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    date_creation = models.DateTimeField(default=timezone.now, verbose_name='Date de création')
    date_mise_a_jour = models.DateTimeField(auto_now=True, verbose_name='Dernière mise à jour')
    est_publie = models.BooleanField(default=True, verbose_name='Publié')
    type_galerie = models.CharField(
        max_length=10, 
        choices=TYPE_CHOICES, 
        default='photo',
        verbose_name='Type de galerie'
    )
    categorie = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='galeries',
        verbose_name='Catégorie'
    )
    
    class Meta:
        verbose_name = 'Galerie'
        verbose_name_plural = 'Galeries'
        ordering = ['-date_creation']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.titre
    
    @property
    def image_couverture(self):
        """Retourne la première image de la galerie comme image de couverture"""
        premiere_image = self.images.first()
        return premiere_image.image if premiere_image else None


class ImageGalerie(models.Model):
    """
    Modèle pour gérer les images d'une galerie
    """
    galerie = models.ForeignKey(
        Galerie, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name='Galerie associée'
    )
    image = models.ImageField(upload_to='galeries/images/', verbose_name='Image')
    legende = models.CharField(max_length=255, blank=True, null=True, verbose_name='Légende')
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    est_principale = models.BooleanField(default=False, verbose_name='Image principale')
    ordre = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')
    
    class Meta:
        verbose_name = 'Image de galerie'
        verbose_name_plural = 'Images de galerie'
        ordering = ['ordre', 'date_ajout']
    
    def __str__(self):
        return f"Image de {self.galerie.titre} - {self.legende or 'Sans titre'}"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'une seule image peut être marquée comme principale
        if self.est_principale:
            ImageGalerie.objects.filter(galerie=self.galerie, est_principale=True).update(est_principale=False)
        super().save(*args, **kwargs)


class Service(models.Model):
    """Modèle pour gérer les services proposés"""
    title = models.CharField(max_length=200, verbose_name='Titre du service')
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name='Slug')
    short_description = models.TextField(verbose_name='Description courte (accueil)')
    description = models.TextField(verbose_name='Description principale (page détaillée)')
    additional_description = models.TextField(verbose_name='Deuxième description (page détaillée)', blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True, help_text='Classe CSS de l\'icône (ex: flaticon-gardening)')
    image = models.ImageField(upload_to='services/', blank=True, null=True, verbose_name='Image principale')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ServiceMedia(models.Model):
    """Modèle pour gérer les médias supplémentaires des services"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='media')
    image = models.ImageField(upload_to='services/media/', verbose_name='Image')
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name='Légende')
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Média pour {self.service.title}"


class Article(models.Model):
    """Modèle pour gérer les articles de blog"""
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
    ]

    title = models.CharField(max_length=255, verbose_name='Titre principal')
    title_2 = models.CharField(max_length=255, blank=True, null=True, verbose_name='Deuxième titre')
    title_3 = models.CharField(max_length=255, blank=True, null=True, verbose_name='Troisième titre')
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name='Slug')
    short_description = models.TextField(blank=True, null=True, verbose_name='Description courte')
    description_1 = models.TextField(verbose_name='Première description', default='')
    description_2 = models.TextField(blank=True, null=True, verbose_name='Deuxième description')
    description_3 = models.TextField(blank=True, null=True, verbose_name='Troisième description')
    description_4 = models.TextField(blank=True, null=True, verbose_name='Quatrième description')
    author = models.CharField(max_length=100, blank=True, null=True, verbose_name='Auteur')
    published_at = models.DateTimeField(default=timezone.now, verbose_name='Date de publication')
    is_published = models.BooleanField(default=True, verbose_name='Publié')
    views = models.PositiveIntegerField(default=0, verbose_name='Nombre de vues')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        verbose_name='Catégorie'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='articles',
        verbose_name='Tags'
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Dernière mise à jour')

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class MediaArticle(models.Model):
    """Modèle pour gérer les médias des articles"""
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Vidéo'),
        ('youtube', 'YouTube'),
        ('vimeo', 'Vimeo'),
    ]

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='media_article',
        verbose_name='Article'
    )
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPES,
        default='image',
        verbose_name='Type de média'
    )
    image = models.ImageField(
        upload_to='articles/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Image'
    )
    video = models.FileField(
        upload_to='articles/videos/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Vidéo'
    )
    video_url = models.URLField(blank=True, null=True, verbose_name='URL de la vidéo')
    caption = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Légende'
    )
    is_featured = models.BooleanField(default=False, verbose_name='Mise en avant')
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')

    class Meta:
        verbose_name = 'Média d\'article'
        verbose_name_plural = 'Médias d\'articles'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Média pour {self.article.title}"

    def clean(self):
        """Validation pour s'assurer qu'un seul type de média est fourni"""
        media_count = sum([
            bool(self.image),
            bool(self.video),
            bool(self.video_url)
        ])

        if media_count > 1:
            raise ValidationError('Vous ne pouvez sélectionner qu\'un seul type de média à la fois.')

        if self.media_type == 'youtube' and not self.video_url:
            raise ValidationError('Une URL YouTube est requise pour ce type de média.')
        elif self.media_type == 'vimeo' and not self.video_url:
            raise ValidationError('Une URL Vimeo est requise pour ce type de média.')
        elif self.media_type == 'video' and not self.video:
            raise ValidationError('Un fichier vidéo est requis pour ce type de média.')
        elif self.media_type == 'image' and not self.image:
            raise ValidationError('Une image est requise pour ce type de média.')


