
from django.contrib import admin
from .models import Setting, Rule, Format, Token

admin.site.register(Setting)

class FormatAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'level')

admin.site.register(Format, FormatAdmin)

class TokenAdmin(admin.ModelAdmin):
    list_display = ('text', 'pos', 'lemma', 'level', 'meaning', 'type')
    search_fields = ('text', 'pos', 'lemma', 'meaning')
    list_filter = ('pos', 'level', 'type')

admin.site.register(Token, TokenAdmin)

class RuleAdmin(admin.ModelAdmin):
    list_display = ('cql', 'getActionCqlDisplay', 'getActionDisplay', 'type', 'order')
    search_fields = ('cql', 'getActionDisplay')
    list_filter = ('type', 'order')

admin.site.register(Rule, RuleAdmin)
