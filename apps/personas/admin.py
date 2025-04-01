from django.contrib import admin
from .models import Persona

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'user', 'rental_budget', 'created')
    list_filter = ('created', 'user')
    search_fields = ('first_name', 'last_name', 'additional_preferences')
    raw_id_fields = ('user',)
