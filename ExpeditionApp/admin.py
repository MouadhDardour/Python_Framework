from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone

from config.helpers import badge
from OffreApp.models import Offre

from .models import Expedition

COULEURS_STATUT = {
    'publiee': '#F0AD4E',
    'attribuee': '#5BC0DE',
    'en_cours': '#0275D8',
    'livree': '#5CB85C',
    'annulee': '#D9534F',
}


class EnRetardFilter(admin.SimpleListFilter):
    title = 'en retard'
    parameter_name = 'en_retard'

    def lookups(self, request, model_admin):
        return [('oui', 'Oui'), ('non', 'Non')]

    def queryset(self, request, queryset):
        aujourdhui = timezone.localdate()
        if self.value() == 'oui':
            return queryset.filter(statut='publiee', date_souhaitee__lt=aujourdhui)
        if self.value() == 'non':
            return queryset.exclude(statut='publiee', date_souhaitee__lt=aujourdhui)
        return queryset


@admin.action(description='Clôturer les expéditions sélectionnées')
def cloturer_expeditions(modeladmin, request, queryset):
    """Only 'en_cours' expeditions are closed. Loop + full_clean() + save(),
    never .update(), so that the business rules of the Models workshop run."""
    cloturees = ignorees = erreurs = 0
    for expedition in queryset:
        if expedition.statut != 'en_cours':
            ignorees += 1
            continue
        expedition.statut = 'livree'
        try:
            expedition.full_clean()
            expedition.save()
            cloturees += 1
        except ValidationError as exc:
            erreurs += 1
            detail = '; '.join(exc.messages)
            modeladmin.message_user(
                request, f'{expedition.reference} : {detail}', level=messages.ERROR
            )
    modeladmin.message_user(
        request,
        f'{cloturees} expédition(s) clôturée(s), {ignorees} ignorée(s) '
        f'(statut différent de en_cours), {erreurs} en erreur.',
        level=messages.SUCCESS if cloturees else messages.WARNING,
    )


class OffreInline(admin.TabularInline):
    """Offers received by an expedition: read-only, with a link to the full record."""
    model = Offre
    fk_name = 'expedition'
    extra = 0
    fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')
    readonly_fields = fields
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = (
        'reference',
        'entreprise',
        'ville_depart',
        'ville_arrivee',
        'statut_colore',
        'statut',
        'date_souhaitee',
    )
    list_filter = ('statut', 'ville_depart', EnRetardFilter)
    search_fields = ('reference', 'entreprise__raison_sociale')
    list_editable = ('statut',)
    ordering = ('-created_at',)
    date_hierarchy = 'date_souhaitee'
    list_per_page = 25
    list_select_related = ('entreprise',)
    autocomplete_fields = ('entreprise',)
    readonly_fields = ('reference', 'created_at', 'updated_at')
    actions = [cloturer_expeditions]
    inlines = [OffreInline]

    fieldsets = (
        ('Trajet', {'fields': ('reference', 'entreprise', 'ville_depart', 'ville_arrivee')}),
        ('Marchandise', {'fields': ('poids_kg', 'date_souhaitee', 'description')}),
        ('Suivi', {'fields': ('statut', 'created_at', 'updated_at')}),
    )

    @admin.display(description='Badge', ordering='statut')
    def statut_colore(self, obj):
        return badge(COULEURS_STATUT.get(obj.statut, '#999999'), obj.get_statut_display())
