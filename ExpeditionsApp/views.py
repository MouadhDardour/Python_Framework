from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import ExpeditionForm
from .models import Expedition


def ajouter_expedition(request):
    if request.method == 'POST':
        form = ExpeditionForm(request.POST)
        if form.is_valid():
            expedition = form.save()
            messages.success(request, f"Expédition {expedition.reference} créée.")
            return redirect('expeditions:detail', reference=expedition.reference)
    else:
        form = ExpeditionForm()
    return render(
        request,
        'form.html',
        {
            'form': form,
            'titre': 'Ajouter une expédition',
            'retour': reverse('expeditions:liste'),
        },
    )


def liste_expeditions(request):
    expeditions = (
        Expedition.objects
        .filter(statut='publiee')
        .select_related('entreprise')
        .order_by('-created_at')
    )
    return render(request, 'expeditions/liste.html', {'expeditions': expeditions})


def detail_expedition(request, reference):
    expedition = get_object_or_404(
        Expedition.objects.select_related('entreprise'), reference=reference
    )
    offres = (
        expedition.offres
        .select_related('transporteur', 'vehicule')
        .order_by('-date_proposition', '-pk')
    )
    return render(
        request,
        'expeditions/detail.html',
        {'expedition': expedition, 'offres': offres},
    )


def modifier_expedition(request, reference):
    expedition = get_object_or_404(Expedition, reference=reference)
    if request.method == 'POST':
        form = ExpeditionForm(request.POST, instance=expedition)
        if form.is_valid():
            form.save()
            messages.success(request, f"Expédition {reference} modifiée.")
            return redirect('expeditions:detail', reference=reference)
    else:
        form = ExpeditionForm(instance=expedition)
    return render(
        request,
        'form.html',
        {
            'form': form,
            'titre': f'Modifier l’expédition {reference}',
            'retour': reverse('expeditions:detail', args=[reference]),
        },
    )


@require_POST  # a GET must never delete anything
def supprimer_expedition(request, reference):
    expedition = get_object_or_404(Expedition, reference=reference)
    if expedition.statut not in ('publiee', 'annulee'):
        messages.error(
            request,
            f"{reference} ne peut plus être supprimée (statut : {expedition.get_statut_display()})."
        )
        return redirect('expeditions:detail', reference=reference)
    expedition.delete()
    messages.success(request, f"Expédition {reference} supprimée.")
    return redirect('expeditions:liste')
