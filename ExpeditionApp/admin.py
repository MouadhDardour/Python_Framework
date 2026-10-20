
from django.contrib import admin
from django.utils import timezone
from .models import Expedition

class EnretardFilter(admin.SimpleListFilter):
    title = 'En retard'
    parameter_name = 'en_retard'

    def lookups(self, request, model_admin):
        return (
            ('oui', 'Oui'),
            ('non', 'Non'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'oui':
            return queryset.filter(date_souhaitee__lt=timezone.now())
        elif self.value() == 'non':
            return queryset.filter(date_souhaitee__gte=timezone.now())
        return queryset

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

    list_filter = ('statut', 'ville_depart', EnretardFilter)

    search_fields = (
        'reference',
        'entreprise__raison_sociale',
    )

    ordering = ('-created_at',)

    date_hierarchy = 'date_souhaitee'

    list_per_page = 25
