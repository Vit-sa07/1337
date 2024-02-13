from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_published', 'created_at')
    list_filter = ('rating', 'created_at', 'is_published')
    search_fields = ('text', 'user__username', 'product__name')
    list_editable = ('is_published',)
    fields = ('product', 'user', 'text', 'rating', 'is_published', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['make_published', 'make_unpublished']

    def make_published(self, request, queryset):
        queryset.update(is_published=True)
    make_published.short_description = "Опубликовать выбранные отзывы"

    def make_unpublished(self, request, queryset):
        queryset.update(is_published=False)
    make_unpublished.short_description = "Скрыть выбранные отзывы"
