from django.db.models import Count
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from ExpeditionsApp.models import Expedition
from .forms import EntrepriseForm
from .models import Entreprise


def ajouter_entreprise(request):
    if request.method == 'POST':
        form = EntrepriseForm(request.POST)
        if form.is_valid():
            entreprise = form.save()
            messages.success(request, f"Entreprise {entreprise.raison_sociale} créée.")
            return redirect('entreprises:detail', pk=entreprise.pk)
    else:
        form = EntrepriseForm()
    return render(
        request,
        'form.html',
        {'form': form, 'titre': 'Ajouter une entreprise', 'retour': reverse('entreprises:liste')},
    )


def liste_entreprises(request):
    entreprises = (
        Entreprise.objects
        .select_related('utilisateur')
        .annotate(nb_vehicules=Count('vehicules', distinct=True))
        .order_by('raison_sociale')
    )
    return render(request, 'entreprises/liste.html', {'entreprises': entreprises})


def modifier_entreprise(request, pk):
    entreprise = get_object_or_404(Entreprise, pk=pk)
    if request.method == 'POST':
        form = EntrepriseForm(request.POST, instance=entreprise)
        if form.is_valid():
            form.save()
            messages.success(request, f"Entreprise {entreprise.raison_sociale} modifiée.")
            return redirect('entreprises:detail', pk=pk)
    else:
        form = EntrepriseForm(instance=entreprise)
    return render(
        request,
        'form.html',
        {
            'form': form,
            'titre': f'Modifier l’entreprise {entreprise.raison_sociale}',
            'retour': reverse('entreprises:detail', args=[pk]),
        },
    )


@require_POST
def supprimer_entreprise(request, pk):
    entreprise = get_object_or_404(Entreprise, pk=pk)
    has_related_records = (
        entreprise.vehicules.exists()
        or Expedition.objects.filter(entreprise=entreprise).exists()
        or entreprise.offres_proposees.exists()
    )
    if has_related_records:
        messages.error(
            request,
            "Cette entreprise possède des véhicules, expéditions ou offres et ne peut pas être supprimée.",
        )
        return redirect('entreprises:detail', pk=pk)
    raison_sociale = entreprise.raison_sociale
    entreprise.delete()
    messages.success(request, f"Entreprise {raison_sociale} supprimée.")
    return redirect('entreprises:liste')


def detail_entreprise(request, pk):
    entreprise = get_object_or_404(Entreprise.objects.select_related('utilisateur'), pk=pk)
    vehicules = entreprise.vehicules.order_by('immatriculation')
    expeditions = Expedition.objects.filter(entreprise=entreprise).order_by('-created_at')
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
