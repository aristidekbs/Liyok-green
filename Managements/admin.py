from django.contrib import admin
from .models import (
    SiteSetting, section, Media,
    TeamMember, ContactMessage, Event, EventMedia, 
    EventRegistration , Service, CarouselImage
)

from django.utils.html import format_html
from django.db.models import Count

# Enregistrement des modèles avec leurs classes d'administration personnalisées
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'email', 'experience', 'slug')
    search_fields = ('name', 'role', 'email')
    list_filter = ('role',)

    # Slug pré-rempli depuis le nom
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Informations principales', {
            'fields': ('name', 'slug', 'role', 'photo', 'experience', 'description')
        }),
        ('Coordonnées', {
            'fields': ('email', 'phone', 'portofolio')
        }),
        ('Réseaux sociaux', {
            'fields': ('facebook', 'twitter', 'linkedin'),
            'classes': ('collapse',)
        }),
    )




class MediaInline(admin.TabularInline):
    model = Media
    extra = 1  # Nombre de lignes vides affichées par défaut
    fields = ('media', 'preview_media', 'main_image')
    readonly_fields = ('preview_media',)

    def preview_media(self, obj):
        """Affiche un aperçu si c'est une image"""
        if obj.media and obj.is_image:
            return mark_safe(f'<img src="{obj.media.url}" style="max-height: 50px;"/>')
        return "-"
    preview_media.short_description = "Aperçu"


class SectionInline(admin.TabularInline):
    model = section
    extra = 0
    fields = ('title', 'subtitle', 'oder', 'edit_link') # J'utilise 'oder' comme dans ton modèle
    readonly_fields = ('edit_link',)
    show_change_link = True # Ajoute un bouton pour aller éditer la section en détail

    def edit_link(self, obj):
        return "Sauvegarde le service pour éditer les médias ici"
    edit_link.short_description = "Détails"

# --- ADMINS ---









# --- 1. Gestion des Médias directement dans la fiche Événement ---
class EventMediaInline(admin.TabularInline):
    model = EventMedia
    extra = 1  # Affiche une ligne vide par défaut
    fields = ('media_type', 'image', 'preview_image', 'video', 'video_url', 'is_featured', 'order')
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 50px; border-radius: 5px;" />', obj.image.url)
        return "-"
    preview_image.short_description = "Aperçu"


# --- 2. Configuration de l'Admin Événement ---
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ('title', 'status_badge', 'start_date', 'location', 'count_registrations', 'is_active')
    
    # Filtres sur le côté droit
    list_filter = ('status', 'is_active', 'start_date', 'is_free', 'registration_required')
    
    # Barre de recherche
    search_fields = ('title', 'location', 'description')
    
    # Remplissage auto du slug
    prepopulated_fields = {'slug': ('title',)}
    
    # On ajoute les médias en bas
    inlines = [EventMediaInline]
    
    # Actions de masse (ex: Publier 10 événements d'un coup)
    actions = ['make_published', 'make_cancelled']

    # Organisation visuelle du formulaire (Indispensable vu le nombre de champs)
    fieldsets = (
        ('Informations Générales', {
            'fields': ('title', 'slug', 'status', 'is_active')
        }),
        ('Dates & Lieu', {
            'fields': (('start_date', 'end_date'), 'location', 'address'),
            'classes': ('collapse',), # On peut replier cette section si besoin
        }),
        ('Contenu', {
            'fields': ('short_description', 'description')
        }),
        ('Prix & Places', {
            'fields': (('price', 'is_free'), 'max_participants')
        }),
        ('Configuration des Inscriptions', {
            'fields': ('registration_required', 'registration_deadline'),
            'description': "Cochez 'Inscription requise' pour activer le formulaire sur le site."
        }),
    )

    # --- Méthodes personnalisées pour l'affichage ---

    def status_badge(self, obj):
        """Affiche le statut avec des couleurs"""
        colors = {
            'draft': 'gray',
            'published': 'green',
            'cancelled': 'red',
            'completed': 'blue',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 15px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Statut"

    def count_registrations(self, obj):
        """Compte les inscrits"""
        count = obj.registrations.count()
        style = "color: red; font-weight: bold;" if obj.max_participants and count >= obj.max_participants else ""
        return format_html('<span style="{}">{} / {}</span>', style, count, obj.max_participants or "∞")
    count_registrations.short_description = "Inscrits"

    # --- Actions personnalisées ---
    def make_published(self, request, queryset):
        queryset.update(status='published')
    make_published.short_description = "Publier les événements sélectionnés"

    def make_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    make_cancelled.short_description = "Annuler les événements sélectionnés"


# --- 3. Configuration de l'Admin Inscriptions ---
@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name_display', 'event', 'email', 'phone', 'status_colored', 'registration_date')
    list_filter = ('event', 'status', 'registration_date')
    search_fields = ('first_name', 'last_name', 'email', 'event__title')
    readonly_fields = ('registration_date',)
    actions = ['mark_confirmed', 'mark_cancelled']

    fieldsets = (
        ('Participant', {
            'fields': (('first_name', 'last_name'), ('email', 'phone'), ('company', 'position'))
        }),
        ('Détails Inscription', {
            'fields': ('event', 'status', 'number_of_people', 'registration_date')
        }),
        ('Interne', {
            'fields': ('special_requirements', 'notes', 'confirmation_sent')
        })
    )

    def full_name_display(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name_display.short_description = "Nom complet"

    def status_colored(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'green',
            'cancelled': 'red',
            'waiting': 'purple',
        }
        return format_html(
            '<b style="color: {};">{}</b>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colored.short_description = "Statut"

    # Actions pour gérer les inscrits
    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_confirmed.short_description = "Confirmer les inscriptions sélectionnées"

    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_cancelled.short_description = "Annuler les inscriptions sélectionnées"



# 1. Configuration du Carousel (pour l'avoir en bas de la page Service)
class CarouselInline(admin.TabularInline):
    model = CarouselImage
    extra = 1  # Affiche une ligne vide prête à être remplie
    fields = ('image', 'order') # Les champs à afficher dans le tableau
    verbose_name = "Image du carousel"
    verbose_name_plural = "Images du carousel"

# 2. Configuration de la page Service
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    # Colonnes visibles dans la liste des services
    list_display = ('name', 'slug', 'created_at')
    
    # Barre de recherche
    search_fields = ('name',)
    
    # Remplissage automatique du slug quand tu tapes le nom (Super pratique !)
    prepopulated_fields = {'slug': ('name',)}

    # Organisation visuelle du formulaire d'édition
    fieldsets = (
        ('En-tête & Images Fixes', {
            'fields': ('name', 'slug', 'main_image', 'secondary_image'),
            'description': "Informations générales et images statiques."
        }),
        ('Contenu Textuel (Rich Text)', {
            'fields': ('intro_content', 'details_content', 'extra_content'),
            'classes': ('wide',), # Prend toute la largeur pour l'éditeur
            'description': "Rédigez vos contenus ici (Titres, paragraphes, listes...)."
        }),
    )

    # On attache le carousel en bas
    inlines = [CarouselInline]

# (Optionnel) Si tu veux voir les images du carousel seules, sinon tu peux supprimer ça
@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ('service', 'order', 'image')
    list_filter = ('service',)






# Enregistrement des modèles avec configuration par défaut
admin.site.register(SiteSetting)
admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(ContactMessage)


# Note: section et Media sont enregistrés via leurs inlines respectifs

