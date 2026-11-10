from django.contrib import admin

from .models import Vehicule


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'type_vehicule', 'capacite_kg', 'entreprise', 'disponible')
    list_filter = ('type_vehicule', 'disponible')
    # search_fields is required here: OffreAdmin uses autocomplete_fields on Vehicule
    search_fields = ('immatriculation', 'entreprise__raison_sociale')
    list_editable = ('disponible',)
    ordering = ('immatriculation',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    list_select_related = ('entreprise',)
    autocomplete_fields = ('entreprise',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Véhicule', {'fields': ('immatriculation', 'type_vehicule', 'capacite_kg')}),
        ('Affectation', {'fields': ('entreprise', 'disponible')}),
        ('Suivi', {'fields': ('created_at', 'updated_at')}),
    )

