from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from .models import Entreprise


def liste_entreprises(request):
    entreprises = (
        Entreprise.objects
        .select_related('utilisateur')
        .annotate(nb_vehicules=Count('vehicules', distinct=True))
        .order_by('raison_sociale')
    )
    return render(request, 'entreprises/liste.html', {'entreprises': entreprises})


def detail_entreprise(request, pk):
    entreprise = get_object_or_404(Entreprise.objects.select_related('utilisateur'), pk=pk)
    vehicules = entreprise.vehicules.order_by('immatriculation')
    expeditions = entreprise.expeditions.order_by('-created_at')
    offres = entreprise.offres_proposees.select_related('expedition').order_by('-date_proposition', '-pk')
    return render(
        request,
        'entreprises/detail.html',
        {
            'entreprise': entreprise,
            'vehicules': vehicules,
            'expeditions': expeditions,
            'offres': offres,
        }
    )
