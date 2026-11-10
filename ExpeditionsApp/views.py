from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Expedition


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
