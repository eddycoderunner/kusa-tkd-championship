from django.contrib import admin
from django.contrib import messages
from django.urls import path, reverse
from django.shortcuts import render
from django.utils.html import format_html

from .models import Competitor, DrawEntry
from .draw import generate_draw
from .views import _build_draw_tree  


@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'seeded_badge', 'reg_no', 'gender',
                    'weight_category', 'school', 'phone')
    list_filter = ('gender', 'weight_category', 'is_seeded', 'school')
    search_fields = ('full_name', 'reg_no', 'school')
    actions = ['regenerate_draw']

    def seeded_badge(self, obj):
        return "S" if obj.is_seeded else ""
    seeded_badge.short_description = "Black belt"

    @admin.action(description="🔄 Regenerate the tournament draw")
    def regenerate_draw(self, request, queryset):
        try:
            warnings = generate_draw()
            if warnings:
                for (g, w), msg in warnings.items():
                    messages.warning(request, f"[{g}/{w}] {msg}")
            messages.success(request, "Draw regenerated successfully.")
        except Exception as e:
            messages.error(request, f"Draw generation failed: {e}")


@admin.register(DrawEntry)
class DrawEntryAdmin(admin.ModelAdmin):
    list_display = ('gender', 'weight_category', 'round_name',
                    'match_number', 'slot', 'side', 'competitor')
    list_filter = ('gender', 'weight_category', 'round_name')
    change_list_template = 'admin/drawentry_changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('bracket-view/', self.admin_site.admin_view(self.bracket_view),
                 name='drawentry_bracket_view'),
        ]
        return custom + urls

    def bracket_view(self, request):
        all_draws = _build_draw_tree()
        context = {
            **self.admin_site.each_context(request),
            'title': 'Bracket view',
            'all_draws': all_draws,
            'opts': self.model._meta,
        }
        return render(request, 'admin/bracket.html', context)