from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import VehiculeForm
from .models import Vehicule


def ajouter_vehicule(request):
    if request.method == 'POST':
        form = VehiculeForm(request.POST)
        if form.is_valid():
            vehicule = form.save()
            messages.success(request, f"Véhicule {vehicule.immatriculation} créé.")
            return redirect('vehicules:detail', pk=vehicule.pk)
    else:
        form = VehiculeForm()
    return render(
        request,
        'form.html',
        {'form': form, 'titre': 'Ajouter un véhicule', 'retour': reverse('vehicules:liste')},
    )


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


def modifier_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if request.method == 'POST':
        form = VehiculeForm(request.POST, instance=vehicule)
        if form.is_valid():
            form.save()
            messages.success(request, f"Véhicule {vehicule.immatriculation} modifié.")
            return redirect('vehicules:detail', pk=pk)
    else:
        form = VehiculeForm(instance=vehicule)
    return render(
        request,
        'form.html',
        {
            'form': form,
            'titre': f'Modifier le véhicule {vehicule.immatriculation}',
            'retour': reverse('vehicules:detail', args=[pk]),
        },
    )


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
