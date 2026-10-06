from django.db import models
from django.core.validators import MinValueValidator
from EntrepriseApp.models import Entreprise
from django.utils import timezone
# Create your models here.
class Expedition(models.Model):
    reference = models.CharField(max_length=100, unique=True)
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    poids_kg = models.DecimalField(max_digits=10, decimal_places=2, validators=[
        MinValueValidator(0, message="Le poids doit être supérieur à 0kg."),
    ])
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
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='expeditions')
    def clean(self):
        super().clean()
        if self.entreprise_id and self.entreprise.type_entreprise != 'chargeur':
            raise ValidationError("une expedition ne peut etre creee que par un chargeur.")
    @classmethod
    def _generate_reference(cls):
        annee = timezone.now().strftime('%y')
        prefix = f"EXP_{annee}"
        dernier=(
            cls.objects.filter(reference__startswith=prefix)
            .order_by('reference')
            .last()
        )
        compteur=(
            int(dernier.reference[-5:]) + 1 if dernier else 1
        )
        if compteur > 99999:
            raise ValueError("Le compteur a dépassé la limite maximale de 99999.")
        return f"{prefix}{compteur:05d}"
    def save(self):
        if self.reference:
            self.reference = self._generate_reference()
        #fct appelee pour appliquer les validateurs
        self.full_clean()
        super().save(*args, **kwargs)