
from django.contrib import admin
from .models import Expedition


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = (
        'reference',
        'entreprise',
        'ville_depart',
        'ville_arrivee',
        'statut',
        'date_souhaitee',
    )

    list_filter = ('statut', 'ville_depart')

    search_fields = (
        'reference',
        'entreprise__raison_sociale',
    )

    ordering = ('-created_at',)

    date_hierarchy = 'date_souhaitee'

    list_per_page = 25
