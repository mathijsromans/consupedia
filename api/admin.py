from api.models import *
from django.contrib import admin


class QuestionmarkEntryAdmin(admin.ModelAdmin):
    model = QuestionmarkEntry
    list_display = ('id', 'name', 'brand', 'score_environment', 'score_social', 'score_animals', 'score_personal_health')


admin.site.register(QuestionMarkQuery)
admin.site.register(JumboQuery)
admin.site.register(AHQuery)
admin.site.register(AHEntry)
admin.site.register(JumboEntry)
admin.site.register(QuestionmarkEntry, QuestionmarkEntryAdmin)
