from django.contrib import admin
from .models import Category, Product, ProductImage, Cart, CartItem


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


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('total_price',)

    def total_price(self, instance):
        """Показать общую цену для каждого товара в корзине."""
        return instance.quantity * instance.product.price

    total_price.short_description = 'Общая цена'


class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ('user', 'total_cart_price')
    search_fields = ('user__username', 'user__email')

    def total_cart_price(self, obj):
        """Подсчитать общую стоимость всех товаров в корзине."""
        return sum(item.total_price() for item in obj.items.all())

    total_cart_price.short_description = 'Общая стоимость корзины'


admin.site.register(Cart, CartAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
