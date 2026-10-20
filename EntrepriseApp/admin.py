from django.contrib import admin
from .models import Entreprise
from .models import Utilisateur 
from .models import Vehicule
from django.contrib.auth.admin import UserAdmin     
class vehiculeInline(admin.TabularInline):
    model = Vehicule
    fields = ('immatriculation', 'type_vehicule', 'capacite_kg', 'disponible')
    extra = 2
    show_change_link = True
class EntrepriseAdmin(admin.ModelAdmin):
    Inlines = [vehiculeInline]
    list_display = ('raison_sociale', 'siret', 'adresse', 'ville', 'code_postal', 'pays')
    search_fields = ('raison_sociale', 'siret', 'ville', 'code_postal', 'pays')
    list_filter = ('pays',)
    ordering = ('raison_sociale',) 
class UtilisateurAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'entreprise')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    ordering = ('username',)

 #Register your models here.
admin.site.register(Entreprise, EntrepriseAdmin)
admin.site.register(Utilisateur, UtilisateurAdmin)