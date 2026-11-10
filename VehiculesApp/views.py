from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Vehicule

def liste_vehicules(request):
    vehicules = Vehicule.objects.select_related('entreprise').order_by('immatriculation')
    return render(request, 'vehicules/liste.html', {'vehicules': vehicules})

def detail_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule.objects.select_related('entreprise'), pk=pk)
    offres = (
        vehicule.offres
        .select_related('expedition', 'transporteur')
        .order_by('-date_proposition', '-pk')
    )
    return render(request, 'vehicules/detail.html', {'vehicule': vehicule, 'offres': offres})

@require_POST
def supprimer_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    try:
        vehicule.delete()
    except ProtectedError:
        # Offre.vehicule uses on_delete=PROTECT
        messages.error(request, "Ce véhicule est lié à des offres : suppression impossible.")
        return redirect('vehicules:detail', pk=pk)
    messages.success(request, f"Véhicule {vehicule.immatriculation} supprimé.")
    return redirect('vehicules:liste')
