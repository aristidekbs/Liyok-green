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
    

class section(models.Model):
    Service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='sections')
    oder = models.IntegerField()
    title = models.CharField(max_length=255 , verbose_name="Titre", blank=True, null=True)
    subtitle = models.CharField(max_length=255 , verbose_name="Sous-titre", blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.title


class Media(models.Model):
    section = models.ForeignKey(section, on_delete=models.CASCADE , related_name='medias')
    media = models.FileField(upload_to='media/')
    main_image = models.BooleanField(default=False)

    @property
    def extension(self):
        name = self.media.name
        return name.split('.')[-1].lower()

    @property
    def is_image(self):
        return self.extension in ["jpg", "jpeg", "png", "gif", "bmp", "webp"]

    @property
    def is_video(self):
        return self.extension in ["mp4", "avi", "mov", "mkv", "wmv"]

    @property
    def is_audio(self):
        return self.extension in ["mp3", "wav", "aac", "ogg", "flac"]

    @property
    def is_document(self):
        return self.extension in ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx"]

    def save(self, *args, **kwargs):

        # Si ce media est défini comme main_image = True
        if self.main_image:
            # Récupération du service lié via la section
            service = self.section.Service

            # Désactivation des autres medias main_image du service
            Media.objects.filter(
                section__Service=service,
                main_image=True
            ).exclude(id=self.id).update(main_image=False)

        super().save(*args, **kwargs)

    


class Banner(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='banners/')
    button_text = models.CharField(max_length=100, blank=True, null=True)
    button_link = models.URLField(blank=True, null=True)
    description = models.TextField(blank = False, null = False , max_length = 300)

    def __str__(self):
        return self.title


class TeamMember(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    role = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='team/')
    phone = models.CharField(max_length=150, blank=False, null=False, default="+228 00 00 00 00")
    email = models.EmailField(blank=False, null=False, default="liyokgreen@gmail.com")
    experience = models.IntegerField(blank=False, null=False, default=2)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    portofolio = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.id}" if self.id else self.name)
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    name = models.CharField(max_length=150 ,)
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







class Service(models.Model):
    """Modèle pour gérer les services proposés"""

    
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



