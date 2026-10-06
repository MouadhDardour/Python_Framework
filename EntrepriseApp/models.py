from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils import timezone
def validate_mail(value):
    if not value:
        raise ValidationError("L'adresse e-mail est obligatoire.")
    if not value.endswith('@gmail.com'):
        raise ValidationError("L'adresse e-mail doit se terminer par '@gmail.com'.")
matricule_fiscale_validator = RegexValidator(
    regex=r'^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$',
    message="Le format du matricule fiscal est invalide."
)
# Create your models here.
class Utilisateur(AbstractUser):
    user_id = models.CharField(primary_key=True,max_length=8)
    email = models.EmailField(unique=True, validators=[validate_mail])
    telephone = models.CharField(max_length=15,blank=True,null=True)
    role = models.CharField(max_length=20,choices=[
        ('admin', 'Admin'),
        ('c', 'Chargeur'),
        ('t', 'Transporteur'),
    ],default='c')
    @classmethod
    def _generate_user_id(cls):
        annee = timezone.now().strftime('%y')
        prefix = f"user{annee}"

        dernier = (
            cls.objects
            .filter(user_id__startswith=prefix)
            .order_by('user_id')
            .last()
        )

        compteur = (
            int(dernier.user_id[-2:]) + 1
            if dernier
            else 0
        )

        if compteur > 99:
            raise ValueError(
                "Le compteur a dépassé la limite maximale de 99."
            )

        return f"{prefix}{compteur:02d}"

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = self._generate_user_id()

        self.full_clean()
        super().save(*args, **kwargs)
class Entreprise(models.Model):
    raison_sociale = models.CharField(max_length=200,blank=False,null=False)
    matricule_fiscale = models.CharField(max_length=17,unique=True, validators=[matricule_fiscale_validator])
    adresse = models.TextField(validators=[
        MinLengthValidator(20, message="L'adresse doit contenir au moins 20 caractères."),
    ])
    type_entreprise = models.CharField(max_length=100,choices=[
        ('c', 'Chargeur'),
        ('t', 'Transporteur'),
        
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    gerant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='entreprise')