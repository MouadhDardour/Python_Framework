import csv

from django.contrib import admin
from django.http import HttpResponse

from config.helpers import badge

from .models import Offre

COULEURS_STATUT = {
    'proposee': '#F0AD4E',
    'acceptee': '#5CB85C',
    'refusee': '#D9534F',
    'retiree': '#777777',
}


@admin.action(description='Exporter la sélection en CSV')
def exporter_offres_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="offres.csv"'
    writer = csv.writer(response)
    writer.writerow(['reference_expedition', 'transporteur', 'prix', 'statut'])
    for offre in queryset.select_related('expedition', 'transporteur'):
        writer.writerow([
            offre.expedition.reference,
            offre.transporteur.raison_sociale,
            offre.prix,
            offre.statut,
        ])
    return response


@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = ('expedition', 'transporteur', 'vehicule', 'prix', 'statut_colore', 'date_proposition')
    list_filter = ('statut', 'expedition__statut')
    search_fields = ('expedition__reference', 'transporteur__raison_sociale')
    ordering = ('-date_proposition',)
    date_hierarchy = 'date_proposition'
    list_per_page = 25
    list_select_related = ('expedition', 'transporteur', 'vehicule')
    autocomplete_fields = ('expedition', 'transporteur', 'vehicule')
    readonly_fields = ('statut_colore', 'date_proposition', 'created_at', 'updated_at')
    actions = [exporter_offres_csv]

    fieldsets = (
        ("Détails de l'offre", {'fields': ('expedition', 'transporteur', 'vehicule')}),
        ('Conditions', {'fields': ('prix', 'delai_jours', 'statut')}),
        ('Suivi', {'fields': ('statut_colore', 'date_proposition', 'created_at', 'updated_at')}),
    )

    @admin.display(description='Statut', ordering='statut')
    def statut_colore(self, obj):
        return badge(COULEURS_STATUT.get(obj.statut, '#999999'), obj.get_statut_display())

    def get_readonly_fields(self, request, obj=None):
        # Once accepted, the price and the lead time can no longer be edited.
        base = list(self.readonly_fields)
        if obj and obj.statut == 'acceptee':
            return base + ['prix', 'delai_jours']
        return base
