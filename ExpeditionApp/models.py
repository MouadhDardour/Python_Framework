from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

from EntrepriseApp.models import Entreprise


class Expedition(models.Model):
    STATUT_CHOICES = [
        ('publiee', 'Publiée'),
        ('attribuee', 'Attribuée'),
        ('en_cours', 'En cours'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]

    # Generated automatically: EXP-AA-NNNNN
    reference = models.CharField(
        max_length=12,
        unique=True,
        blank=True,
        editable=False,
        validators=[RegexValidator(r'^EXP-\d{2}-\d{5}$', "Format attendu : EXP-AA-NNNNN")],
    )
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    poids_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    date_souhaitee = models.DateField()
    description = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='publiee')
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='expéditions',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def generer_reference():
        """EXP + AA (2-digit year) + NNNNN (00001-99999, restarts every year)."""
        prefixe = f"EXP-{timezone.now().strftime('%y')}-"
        derniere = (
            Expedition.objects.filter(reference__startswith=prefixe)
            .order_by('-reference')
            .first()
        )
        numero = int(derniere.reference[-5:]) + 1 if derniere else 1
        if numero > 99999:
            raise ValidationError("Compteur d'expéditions épuisé pour cette année.")
        return f"{prefixe}{numero:05d}"

    def clean(self):
        if self.entreprise_id and self.entreprise.type_entreprise != 'chargeur':
            raise ValidationError(
                "Une expédition doit être publiée par une entreprise de type chargeur."
            )

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generer_reference()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.reference
