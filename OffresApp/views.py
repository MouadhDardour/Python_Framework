from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Offre


def liste_offres(request):
    offres = (
        Offre.objects
        .select_related('expedition', 'transporteur', 'vehicule')
        .order_by('-date_proposition', '-pk')
    )
    return render(request, 'offres/liste.html', {'offres': offres})


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
