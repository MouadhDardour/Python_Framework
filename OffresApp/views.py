from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import OffreForm
from .models import Offre


def ajouter_offre(request):
    if request.method == 'POST':
        form = OffreForm(request.POST)
        if form.is_valid():
            offre = form.save()
            messages.success(request, f"Offre #{offre.pk} créée.")
            return redirect('offres:detail', pk=offre.pk)
    else:
        form = OffreForm()
    return render(
        request,
        'form.html',
        {'form': form, 'titre': 'Ajouter une offre', 'retour': reverse('offres:liste')},
    )


def liste_offres(request):
    offres = (
        Offre.objects
        .select_related('expedition', 'transporteur', 'vehicule')
        .order_by('-date_proposition', '-pk')
    )
    return render(request, 'offres/liste.html', {'offres': offres})


def modifier_offre(request, pk):
    offre = get_object_or_404(Offre, pk=pk)
    if offre.statut == 'acceptee':
        messages.error(request, "Une offre acceptée ne peut pas être modifiée.")
        return redirect('offres:detail', pk=pk)
    if request.method == 'POST':
        form = OffreForm(request.POST, instance=offre)
        if form.is_valid():
            form.save()
            messages.success(request, f"Offre #{pk} modifiée.")
            return redirect('offres:detail', pk=pk)
    else:
        form = OffreForm(instance=offre)
    return render(
        request,
        'form.html',
        {
            'form': form,
            'titre': f'Modifier l’offre #{pk}',
            'retour': reverse('offres:detail', args=[pk]),
        },
    )


def detail_offre(request, pk):
    offre = get_object_or_404(
        Offre.objects.select_related('expedition', 'transporteur', 'vehicule'), pk=pk
    )
    return render(request, 'offres/detail.html', {'offre': offre})


@require_POST
def supprimer_offre(request, pk):
    offre = get_object_or_404(Offre, pk=pk)
    if offre.statut == 'acceptee':
        messages.error(request, "Une offre acceptée ne peut pas être supprimée.")
        return redirect('offres:detail', pk=pk)
    offre.delete()
    messages.success(request, f"Offre #{pk} supprimée.")
    return redirect('offres:liste')
