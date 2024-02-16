from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Количество дополнительных форм для загрузки изображений


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ]
    list_display = ('name', 'price', 'available', 'created_at', 'updated_at')
    list_filter = ('available', 'created_at', 'updated_at')
    list_editable = ('price', 'available')
    search_fields = ('name', 'description')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
