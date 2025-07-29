from django.contrib import admin
from .models import ItemAcademia

# Register your models here.
admin.site.register(ItemAcademia)

class ItemAcademiaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)
    ordering = ('nome',)
    list_filter = ('nome',)

    fieldsets = (
        (None, {
            'fields': ('nome', 'descricao', 'imagem')
        }),
    )