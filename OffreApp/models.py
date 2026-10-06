from django.db import models
from vehiculeApp.models import Vehicule
from ExpeditionApp.models import Expedition
from EntrepriseApp.models import Entreprise
# Create your models here.
class Offre(models.Model):
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    delai_jours = models.IntegerField()
    sstatut = models.CharField(max_length=50, choices=[
        ('p', 'Proposee'),
        ('a', 'Acceptee'),
        ('r', 'Refusee'),
        ('c', 'Annulee'),
    ])
    date_proposition = models.DateField()
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='offres')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expedition = models.ForeignKey(Expedition, on_delete=models.CASCADE, related_name='offres')
    transporteur = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='offres')