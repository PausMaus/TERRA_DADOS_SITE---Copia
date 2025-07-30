from django.contrib import admin
from .models import Question, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']



admin.site.register(Question, QuestionAdmin)
admin.site.site_header = "TERRA DADOS SITE Admin"
admin.site.site_title = "TERRA DADOS SITE Admin Portal"
admin.site.index_title = "Welcome to the TERRA DADOS SITE Admin Portal"


# Register your models here.
