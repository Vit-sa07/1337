from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'available', 'created_at']
    list_filter = ['available', 'created_at', 'category']
    search_fields = ['name', 'description', 'category__name']
    date_hierarchy = 'created_at'
    ordering = ['name']
    fields = ['name', 'category', 'description', 'price', 'available']
