from django import forms

from EntreprisesApp.models import Entreprise
from .models import Vehicule


class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = ['immatriculation', 'type_vehicule', 'capacite_kg', 'disponible', 'entreprise']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['entreprise'].queryset = Entreprise.objects.filter(
            type_entreprise='transporteur'
        )
