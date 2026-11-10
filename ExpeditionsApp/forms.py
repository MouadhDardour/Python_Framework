from django import forms
from EntreprisesApp.models import Entreprise
from .models import Expedition


class ExpeditionForm(forms.ModelForm):
    class Meta:
        model = Expedition
        fields = ['entreprise', 'ville_depart', 'ville_arrivee', 'poids_kg',
                  'date_souhaitee', 'description', 'statut']
        widgets = {
            'date_souhaitee': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['entreprise'].queryset = Entreprise.objects.filter(type_entreprise='chargeur')