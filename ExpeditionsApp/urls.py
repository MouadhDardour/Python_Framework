from django.urls import path
from . import views

app_name = 'expeditions'

urlpatterns = [
    path('', views.liste_expeditions, name='liste'),
    path('ajouter/', views.ajouter_expedition, name='ajouter'),
    path('<str:reference>/', views.detail_expedition, name='detail'),
    path('<str:reference>/modifier/', views.modifier_expedition, name='modifier'),
    path('<str:reference>/supprimer/', views.supprimer_expedition, name='supprimer'),
]
