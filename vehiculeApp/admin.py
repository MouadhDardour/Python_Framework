from django.contrib import admin
from .models import Vehicule


# Register your models here.
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'type_vehicule', 'capacite_kg', 'disponible')
    fieldsets = (
            ('Identification', {
                'fields': ('immatriculation', 'type_vehicule', 'capacite_kg')
            }),
            ('Statut et rattachement', {
                'fields': ('disponibile', 'entreprise')
            }),
            ('Horodatage', {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',),
            }),
        )
    
admin.site.register(Vehicule, VehiculeAdmin)
