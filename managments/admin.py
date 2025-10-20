from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline
from .models import (
    Event, EventMedia, EventRegistration,
    SiteSetting, Banner, Testimonial,
    ContactMessage, Project, ProjectMedia,
    Category, Galerie, ImageGalerie,
    Service, ServiceMedia, TeamMember, Tag,
    Article, MediaArticle
)

# Inline Classes

class EventMediaInline(TabularInline):
    model = EventMedia
    extra = 1
    fields = ('media_type', 'image', 'video', 'video_url', 'caption', 'is_featured', 'order')
    readonly_fields = ('preview',)
    
    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px;" />')
        return "Aperçu non disponible"
    preview.short_description = 'Aperçu'

class ProjectMediaInline(TabularInline):
    model = ProjectMedia
    extra = 1
    fields = ('image', 'video', 'video_url')


# Admin Classes
@admin.register(SiteSetting)
class SiteSettingAdmin(ModelAdmin):
    list_display = ("site_name", "email_contact", "phone_contact", "logo_preview")
    search_fields = ("site_name",)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="80" style="border-radius: 8px;" />', obj.logo.url)
        return "Aucun logo"
    logo_preview.short_description = "Logo"

@admin.register(Banner)
class BannerAdmin(ModelAdmin):
    list_display = ('title', 'subtitle', 'button_text', 'button_link')
    search_fields = ('title', 'subtitle')
    list_filter = ('button_text',)

@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ('name', 'role', 'photo_preview')
    search_fields = ('name', 'role')
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.photo.url)
        return "Pas de photo"
    photo_preview.short_description = "Photo"

@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ('name', 'email', 'subject', 'sent_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('sent_at',)

class EventRegistrationInline(TabularInline):
    model = EventRegistration
    extra = 0
    readonly_fields = ('registration_date', 'status_badge')
    fields = ('first_name', 'last_name', 'email', 'phone', 'number_of_people', 'status_badge', 'registration_date')
    
    def status_badge(self, obj):
        status_classes = {
            'pending': 'warning',
            'confirmed': 'success',
            'waiting': 'info'
        }
        return mark_safe(
            f'<span class="badge bg-{status_classes.get(obj.status, "secondary")}">'
            f'{obj.get_status_display()}</span>'
        )
    status_badge.short_description = 'Statut'
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Event)
class EventAdmin(ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'location', 'status_badge', 'registration_status', 'participants_count')
    list_filter = ('status', 'is_active', 'registration_required', 'start_date')
    search_fields = ('title', 'short_description', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at', 'status_badge')
    date_hierarchy = 'start_date'
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'slug', 'short_description', 'description')
        }),
        ('Dates et lieu', {
            'fields': ('start_date', 'end_date', 'location', 'address')
        }),
        ('Inscriptions', {
            'fields': (
                'registration_required', 'registration_deadline', 'max_participants',
                'price', 'is_free'
            )
        }),
        ('Statut et visibilité', {
            'fields': ('status', 'is_active', 'created_at', 'updated_at')
        }),
    )
    inlines = [EventMediaInline, EventRegistrationInline]
    prepopulated_fields = {'slug': ('title',)}
    
    def status_badge(self, obj):
        status_classes = {
            'draft': 'secondary',
            'published': 'success',
            'cancelled': 'danger',
            'completed': 'info'
        }
        return mark_safe(
            f'<span class="badge bg-{status_classes.get(obj.status, "secondary")}">'
            f'{obj.get_status_display()}</span>'
        )
    status_badge.short_description = 'Statut'
    
    def registration_status(self, obj):
        if not obj.registration_required:
            return 'Inscriptions non requises'
            
        if obj.registration_open:
            return mark_safe('<span class="text-success">Inscriptions ouvertes</span>')
        return mark_safe('<span class="text-muted">Inscriptions fermées</span>')
    registration_status.short_description = 'État des inscriptions'
    
    def participants_count(self, obj):
        confirmed = obj.registrations.filter(status='confirmed').count()
        waiting = obj.registrations.filter(status='waiting').count()
        
        if obj.max_participants:
            return f'{confirmed}/{obj.max_participants} inscrits' + (f' (+{waiting} en attente)' if waiting else '')
        return f'{confirmed} inscrits' + (f' (+{waiting} en attente)' if waiting else '')
    participants_count.short_description = 'Participants'

@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title', 'description')
    list_filter = ('date',)
    inlines = [ProjectMediaInline]


class ImageGalerieInline(TabularInline):
    model = ImageGalerie
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" height="auto" />')
        return "Aucune image"
    image_preview.short_description = 'Aperçu'

@admin.register(Galerie)
class GalerieAdmin(ModelAdmin):
    list_display = ('titre', 'type_galerie', 'categorie', 'date_creation', 'est_publie')
    list_filter = ('type_galerie', 'est_publie', 'categorie')
    search_fields = ('titre', 'description')
    prepopulated_fields = {'slug': ('titre',)}
    inlines = [ImageGalerieInline]
    date_hierarchy = 'date_creation'
    list_editable = ('est_publie',)
    readonly_fields = ('date_creation', 'date_mise_a_jour')
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'slug', 'description', 'type_galerie', 'categorie')
        }),
        ('Publication', {
            'fields': ('est_publie', 'date_creation', 'date_mise_a_jour')
        }),
    )

@admin.register(ImageGalerie)
class ImageGalerieAdmin(ModelAdmin):
    list_display = ('__str__', 'galerie', 'legende', 'est_principale', 'date_ajout')
    list_filter = ('est_principale', 'galerie')
    search_fields = ('legende', 'galerie__titre')
    list_editable = ('est_principale', 'legende')
    readonly_fields = ('image_preview', 'date_ajout')
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="150" height="auto" style="max-height: 150px;" />')
        return "Aucune image"
    image_preview.short_description = 'Aperçu'


class ServiceMediaInline(TabularInline):
    model = ServiceMedia
    extra = 1
    fields = ('image', 'caption', 'order')
    ordering = ('order',)


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    list_display = ('title', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'short_description', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ServiceMediaInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'short_description', 'description', 'is_active', 'order')
        }),
        ('Médias', {
            'fields': ('icon', 'image'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ServiceMedia)
class ServiceMediaAdmin(ModelAdmin):
    list_display = ('__str__', 'service', 'order', 'created_at')
    list_filter = ('service', 'created_at')
    search_fields = ('service__title', 'caption')
    ordering = ('service', 'order', '-created_at')
    list_editable = ('order',)
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px;" />')
        return "Aucune image"
    image_preview.short_description = 'Aperçu'

@admin.register(TeamMember)
class TeamMemberAdmin(ModelAdmin):
    list_display = ('name', 'role', 'photo_preview')
    search_fields = ('name', 'role', 'description')
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 50%;" />', obj.photo.url)
        return "Aucune photo"
    photo_preview.short_description = 'Photo'



@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    search_fields = ('name', 'description')
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


class MediaArticleInline(TabularInline):
    model = MediaArticle
    extra = 1
    fields = ('media_type', 'image', 'video', 'video_url', 'caption', 'is_featured', 'order')
    ordering = ('order',)


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'published_at', 'views')
    list_filter = ('is_published', 'category', 'published_at', 'tags')
    search_fields = ('title', 'short_description', 'description_1', 'author')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    filter_horizontal = ('tags',)
    readonly_fields = ('created_at', 'updated_at', 'views')
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'title_2', 'title_3', 'slug', 'short_description', 'author')
        }),
        ('Descriptions', {
            'fields': ('description_1', 'description_2', 'description_3', 'description_4'),
            'classes': ('collapse',)
        }),
        ('Publication', {
            'fields': ('is_published', 'published_at', 'category', 'tags')
        }),
        ('Statistiques', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [MediaArticleInline]


@admin.register(MediaArticle)
class MediaArticleAdmin(ModelAdmin):
    list_display = ('__str__', 'article', 'media_type', 'is_featured', 'order', 'created_at')
    list_filter = ('media_type', 'is_featured', 'created_at')
    search_fields = ('article__title', 'caption')
    ordering = ('article', 'order', '-created_at')
    list_editable = ('order', 'is_featured')

