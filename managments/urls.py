from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('about/', views.About, name='about'),
    path('contact/', views.Contact, name='contact'),
    path('event/', views.event_list, name='event'),
    path('event/<slug:slug>/', views.event_detail, name='event-detail'),
    # URLs pour les services
    path('services/', views.service_list, name='service'),
    path('services/<slug:slug>/', views.service_detail, name='service-detail'),
    
    # URLs pour la galerie
    path('galerie/', views.galery_categories, name='galery_categories'),
    path('galerie/<slug:category_slug>/<slug:galery_slug>/', views.galerie_detail, name='galerie_detail'),

    # URLs pour les articles
    path('articles/', views.article_list, name='article_list'),
    path('articles/category/<slug:category_slug>/', views.article_list, name='article_list_by_category'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),

    path('articles/', views.article_list, name='article_list'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),

    # URLs pour les documents
    path('documents/', views.document_list, name='document_list'),
    path('documents/<slug:slug>/', views.document_detail, name='document_detail'),
    path('documents/<slug:slug>/download/', views.document_download, name='document_download'),
]