from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, AddToCartView, RemoveFromCartView, CartView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/remove/<int:telegram_id>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('cart/<int:telegram_id>/', CartView.as_view(), name='cart'),
]
