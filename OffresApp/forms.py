from django import forms

from EntreprisesApp.models import Entreprise
from ExpeditionsApp.models import Expedition
from VehiculesApp.models import Vehicule
from .models import Offre


class OffreForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = ['expedition', 'transporteur', 'vehicule', 'prix', 'delai_jours']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transporteur'].queryset = Entreprise.objects.filter(
            type_entreprise='transporteur'
        )
        self.fields['expedition'].queryset = Expedition.objects.select_related('entreprise')
        self.fields['vehicule'].queryset = Vehicule.objects.select_related('entreprise')
