from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from EntreprisesApp.models import Entreprise

# Business rule 7: the vehicle type caps the weight it can carry (kg).
CAPACITE_MAX_PAR_TYPE = {
    'camionnette': 1500,
    'fourgon': 3500,
    'camion_porteur': 19000,
    'semi_remorque': 26000,
}


class Vehicule(models.Model):
    TYPE_CHOICES = [
        ('camionnette', 'Camionnette / utilitaire léger'),
        ('fourgon', 'Fourgon'),
        ('camion_porteur', 'Camion porteur'),
        ('semi_remorque', 'Semi-remorque'),
    ]

    immatriculation = models.CharField(max_length=20, unique=True)
    type_vehicule = models.CharField(max_length=20, choices=TYPE_CHOICES)
    capacite_kg = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    disponible = models.BooleanField(default=True)
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='vehicules',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.entreprise_id and self.entreprise.type_entreprise != 'transporteur':
            raise ValidationError(
                "Un véhicule doit appartenir à une entreprise de type transporteur."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.immatriculation} ({self.get_type_vehicule_display()})"