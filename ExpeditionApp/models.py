from django.db import models
# Create your models here.
class Expedition(models.Model):
    reference = models.CharField(max_length=100, unique=True)
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    poids_kg = models.DecimalField(max_digits=10, decimal_places=2)
    date_souhaitee = models.DateField()
    description = models.TextField()
    statut = models.CharField(max_length=50, choices=[
        ('p', 'Publiee'),
        ('a', 'Attribuee'),
        ('t', 'Terminee'),
        ('c', 'Annulee'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
