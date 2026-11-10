from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from vehiculeApp.models import Vehicule

from .models import Entreprise, Utilisateur


class UtilisateurCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = ('username', 'email', 'role', 'telephone')


class UtilisateurChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Utilisateur


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    add_form = UtilisateurCreationForm
    form = UtilisateurChangeForm
    model = Utilisateur

    list_display = ('user_id', 'username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('user_id', 'username', 'email')
    ordering = ('user_id',)
    readonly_fields = ('user_id', 'created_at', 'updated_at')

    fieldsets = UserAdmin.fieldsets + (
        ('TransConnect', {'fields': ('user_id', 'role', 'telephone', 'created_at', 'updated_at')}),
    )
    
    # Override add_fieldsets to avoid referencing built-in fields like 'usable_password' that your custom form doesn't use
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'telephone', 'password1', 'password2'),
        }),
    )

class VehiculeInline(admin.TabularInline):
    model = Vehicule
    extra = 0
    fields = ('immatriculation', 'type_vehicule', 'capacite_kg', 'disponible')


@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('raison_sociale', 'matricule_fiscal', 'type_entreprise', 'utilisateur', 'created_at')
    list_filter = ('type_entreprise',)
    # search_fields is required here: other admins use autocomplete_fields on Entreprise
    search_fields = ('raison_sociale', 'matricule_fiscal')
    ordering = ('raison_sociale',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    list_select_related = ('utilisateur',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [VehiculeInline]

    fieldsets = (
        ('Identité', {'fields': ('raison_sociale', 'matricule_fiscal', 'type_entreprise')}),
        ('Contact', {'fields': ('adresse', 'utilisateur')}),
        ('Suivi', {'fields': ('created_at', 'updated_at')}),
    )
