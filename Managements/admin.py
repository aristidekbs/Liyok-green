from django.contrib import admin
from .models import (
    SiteSetting, Service, section, Media, Banner, 
    TeamMember, ContactMessage, Event, EventMedia, 
    EventRegistration
)

from django.utils.html import format_html


class MediaInline(admin.TabularInline):
    model = Media
    extra = 1
    fields = ('media', 'main_image', 'order')
    readonly_fields = ('preview',)
    
    def preview(self, obj):
        if obj.media:
            if obj.is_image:
                return format_html('<img src="{}" style="max-height: 100px;" />', obj.media.url)
            return f"Fichier: {obj.media.name}"
        return "Aucun média"
    preview.short_description = 'Aperçu'


class SectionInline(admin.TabularInline):
    model = section
    extra = 1
    show_change_link = True
    inlines = [MediaInline]  # Ceci ne fonctionne pas directement, nécessite une solution personnalisée
    fields = ('title', 'subtitle', 'order', 'content')


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order', 'created_at')
    list_editable = ('is_active', 'order')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SectionInline]


class EventMediaInline(admin.TabularInline):
    model = EventMedia
    extra = 1
    fields = ('media_type', 'image', 'video', 'video_url', 'caption', 'is_featured', 'order')
    readonly_fields = ('preview',)
    
    def preview(self, obj):
        if obj.media_type == 'image' and obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "Aperçu non disponible"
    preview.short_description = 'Aperçu'


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'location', 'status', 'is_active')
    list_filter = ('status', 'is_active', 'start_date')
    search_fields = ('title', 'location', 'description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_date'
    inlines = [EventMediaInline]
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'slug', 'short_description', 'description')
        }),
        ('Date et lieu', {
            'fields': ('start_date', 'end_date', 'location', 'address')
        }),
        ('Paramètres', {
            'fields': ('status', 'is_active', 'is_free', 'price', 'registration_required', 'registration_deadline')
        }),
    )


# Enregistrement des modèles avec leurs classes d'administration personnalisées
admin.site.register(Service, ServiceAdmin)
admin.site.register(Event, EventAdmin)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'email', 'experience', 'slug')
    search_fields = ('name', 'role', 'email')
    list_filter = ('role',)

    # Le slug sera généré automatiquement depuis name
    prepopulated_fields = {'slug': ('name',)}

    # Retirer readonly_fields ici !
    # readonly_fields = ('slug',)

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

    def get_readonly_fields(self, request, obj=None):
        """Rendre slug readonly uniquement APRÈS la création"""
        if obj:
            return ('slug',)
        return ()





# Enregistrement des modèles avec configuration par défaut
admin.site.register(SiteSetting)
admin.site.register(Banner)
admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(ContactMessage)
admin.site.register(EventRegistration)

# Note: section et Media sont enregistrés via leurs inlines respectifs