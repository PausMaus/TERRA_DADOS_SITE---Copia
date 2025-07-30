from django.contrib import admin
from .models import ItemAcademia, Equipamento, Area, Professor, Exercicio, Treino

# Register your models here.
admin.site.register(ItemAcademia)
admin.site.register(Equipamento)
admin.site.register(Area)
admin.site.register(Exercicio)
admin.site.register(Professor)
admin.site.register(Treino)


class AreaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', )
    search_fields = ('nome',)
    ordering = ('nome',)
    list_filter = ('nome',)

    fieldsets = (
        (None, {
            'fields': ('nome', 'descricao', 'imagem')
        }),
    )


class ItemAcademiaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', )
    search_fields = ('nome',)
    ordering = ('nome',)
    list_filter = ('nome',)

    fieldsets = (
        (None, {
            'fields': ('nome', 'descricao', 'imagem')
        }),
    )


class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'area', )
    search_fields = ('nome', 'tipo')
    ordering = ('nome',)
    list_filter = ('tipo',)

    fieldsets = (
        (None, {
            'fields': ('nome', 'descricao', 'imagem', 'tipo')
        }),
    )

class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especialidade', )
    search_fields = ('nome', 'especialidade')
    ordering = ('nome',)
    list_filter = ('especialidade',)

    fieldsets = (
        (None, {
            'fields': ('nome', 'descricao', 'imagem', 'especialidade')
        }),
    )


class ExercicioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'duracao', 'repeticoes', 'series', 'dificuldade', )
    search_fields = ('nome', 'dificuldade')
    ordering = ('nome',)
    list_filter = ('dificuldade',)

    fieldsets = (
        (None, {
            'fields': ('nome', 'descricao', 'imagem', 'duracao', 'repeticoes', 'series', 'equipamento', 'professor', 'area', 'dificuldade')
        }),
    )

class TreinoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', 'data', 'duracao', )
    search_fields = ('nome', 'descricao')
    ordering = ('data',)
    list_filter = ('data',)

    fieldsets = (
        (None, {
            'fields': ('nome', 'descricao', 'data', 'duracao', 'exercicios')
        }),
    )