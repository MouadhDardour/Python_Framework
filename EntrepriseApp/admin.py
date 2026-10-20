from django.contrib import admin
from .models import Entreprise
from .models import Utilisateur
admin.site.register(Entreprise)

class userAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'email', 'telephone', 'is_active', 'is_superuser', 'role')
    list_editable = ('username', 'is_active', 'is_superuser',)
    search_fields = ('user_id', 'username', 'email',)
    list_filter = ('is_active', 'is_superuser', 'role',)
# Register your models here.
admin.site.register(Utilisateur, userAdmin)