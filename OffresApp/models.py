from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction

from EntreprisesApp.models import Entreprise
from ExpeditionsApp.models import Expedition
from VehiculesApp.models import CAPACITE_MAX_PAR_TYPE, Vehicule


class Offre(models.Model):
    STATUT_CHOICES = [
        ('proposee', 'Proposée'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('retiree', 'Retirée'),
    ]

    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    delai_jours = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='proposee')
    date_proposition = models.DateField(auto_now_add=True)
    expedition = models.ForeignKey(
        Expedition,
        on_delete=models.CASCADE,
        related_name='offres',
    )
    transporteur = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='offres_proposees',
    )
    vehicule = models.ForeignKey(
        Vehicule,
        on_delete=models.PROTECT,
        related_name='offres',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _ancien_statut(self):
        if not self.pk:
            return None
        return Offre.objects.filter(pk=self.pk).values_list('statut', flat=True).first()

    def clean(self):
        erreurs = []
        nouvelle = self._state.adding

        # Rule 1: only a transporteur can create an offer
        if self.transporteur_id and self.transporteur.type_entreprise != 'transporteur':
            erreurs.append("Une offre ne peut être créée que par une entreprise de type transporteur.")

        # Rule 2: the vehicle must belong to the offer's transporteur
        if self.transporteur_id and self.vehicule_id:
            if self.vehicule.entreprise_id != self.transporteur_id:
                erreurs.append("Le véhicule doit appartenir au transporteur de l'offre.")

        # Rule 6: an unavailable vehicle cannot be proposed on a new offer
        if nouvelle and self.vehicule_id and not self.vehicule.disponible:
            erreurs.append("Ce véhicule n'est pas disponible.")

        if self.expedition_id:
            expedition = self.expedition

            # Rule 3: only a 'publiee' expedition can receive new offers
            if nouvelle and expedition.statut != 'publiee':
                erreurs.append("Cette expédition n'est plus publiée : elle ne peut plus recevoir d'offres.")

            # Rule 4: no two active 'proposee' offers from one company on one expedition
            if self.statut == 'proposee' and self.transporteur_id:
                doublon = Offre.objects.filter(
                    expedition=expedition,
                    transporteur_id=self.transporteur_id,
                    statut='proposee',
                ).exclude(pk=self.pk)
                if doublon.exists():
                    erreurs.append("Ce transporteur a déjà une offre proposée sur cette expédition.")

            # Accepting is only possible while the expedition is still 'publiee'
            if self.statut == 'acceptee' and self._ancien_statut() != 'acceptee':
                if expedition.statut != 'publiee':
                    erreurs.append("Une offre ne peut être acceptée que si l'expédition est encore publiée.")

            # Rule 7: vehicle type + capacity must be compatible with the weight
            if self.vehicule_id:
                plafond = min(
                    self.vehicule.capacite_kg,
                    CAPACITE_MAX_PAR_TYPE[self.vehicule.type_vehicule],
                )
                if expedition.poids_kg > plafond:
                    erreurs.append(
                        f"Véhicule incompatible : l'expédition pèse {expedition.poids_kg} kg "
                        f"et ce véhicule ({self.vehicule.get_type_vehicule_display()}) "
                        f"ne peut en transporter que {plafond}."
                    )

        if erreurs:
            raise ValidationError(erreurs)

    def save(self, *args, **kwargs):
        self.full_clean()
        ancien_statut = self._ancien_statut()
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.statut == 'acceptee' and ancien_statut != 'acceptee':
                self._cascade_acceptation()

    def _cascade_acceptation(self):
        """Rule 5: accepting an offer awards the expedition and refuses the others."""
        expedition = self.expedition
        expedition.statut = 'attribuee'
        expedition.save()

        autres = Offre.objects.filter(expedition=expedition, statut='proposee').exclude(pk=self.pk)
        for autre in autres:
            autre.statut = 'refusee'
            autre.save()

        # Our design choice: the awarded vehicle is no longer available
        # (the integrity check "availability inconsistency" relies on it).
        self.vehicule.disponible = False
        self.vehicule.save()

    def __str__(self):
        return f"Offre {self.pk} ({self.get_statut_display()})"
