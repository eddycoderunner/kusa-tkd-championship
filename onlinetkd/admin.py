from django.contrib import admin
from django.utils.html import format_html
from .models import Competitor, DrawEntry

@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'seeded_badge', 'reg_no', 'gender', 'weight_category', 'school', 'phone')
    list_filter = ('gender', 'weight_category', 'is_seeded', 'school')
    search_fields = ('full_name', 'reg_no', 'school')

    def seeded_badge(self, obj):
        return "S" if obj.is_seeded else ""
    seeded_badge.short_descripton = "Seed"


@admin.register(DrawEntry)
class DrawEntryAdmin(admin.ModelAdmin):
    list_display = ('gender', 'weight_category', 'round_name', 'match_number', 'slot', 'competitor')
    list_filter = ('gender', 'weight_category', 'round_name')