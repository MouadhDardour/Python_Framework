from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils import timezone
def valider_email_gmail(value):
    """Only gmail.com addresses are accepted."""
    if not value.lower().endswith('@gmail.com'):
        raise ValidationError(
            "Seuls les emails appartenant au domaine gmail.com sont acceptés."
        )


class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('chargeur', 'Chargeur'),
        ('transporteur', 'Transporteur'),
        ('admin', 'Administrateur'),
    ]

    # Custom PK "AAuserNN" (ex. 26user00), replaces the default id.
    user_id = models.CharField(max_length=8, primary_key=True, editable=False)
    email = models.EmailField(unique=True, validators=[valider_email_gmail])
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='chargeur')
    telephone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def generer_user_id(cls):
        """AA (2-digit year) + 'user' + NN (00-99, restarts every year)."""
        prefixe = f"{timezone.now().strftime('%y')}user"
        dernier = (
            cls.objects.filter(user_id__startswith=prefixe)
            .order_by('-user_id')
            .first()
        )
        numero = int(dernier.user_id[-2:]) + 1 if dernier else 0
        if numero > 99:
            raise ValidationError("Compteur utilisateurs épuisé pour cette année (00-99).")
        return f"{prefixe}{numero:02d}"

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = self.generer_user_id()
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_id} - {self.username}"

# 7 digits + key letter + VAT letter + legal-category letter + 3 digits (with optional separators)
MATRICULE_REGEX = r'^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$'


class Entreprise(models.Model):
    TYPE_CHOICES = [
        ('chargeur', 'Chargeur'),
        ('transporteur', 'Transporteur'),
    ]

    raison_sociale = models.CharField(max_length=150)
    matricule_fiscal = models.CharField(
        max_length=17,
        unique=True,
        validators=[
            RegexValidator(
                regex=MATRICULE_REGEX,
                message="Matricule fiscal invalide (ex. 1234567AAM000 ou 1234567/A/A/M/000).",
            )
        ],
    )
    type_entreprise = models.CharField(max_length=20, choices=TYPE_CHOICES)
    adresse = models.TextField(validators=[MinLengthValidator(20)])
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='entreprise',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.raison_sociale