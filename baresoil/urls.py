from django.urls import path
from .import views

urlpatterns = [
    path('home/',views.home, name='home'),
    path('about/',views.about, name='about'),
    path('latest/',views.latest, name='latest'),
    path('ndvi/',views.ndvi, name='ndvi'),
]