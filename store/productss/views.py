from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Category, Product, ProductImage
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer, CartSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem, Product
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        """
        Переопределение метода get_queryset для фильтрации товаров по категории.
        """
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')
        if category_id is not None:
            queryset = queryset.filter(category__id=category_id, available=True)
        return queryset

    def create(self, request, *args, **kwargs):
        product_serializer = ProductSerializer(data=request.data)
        if product_serializer.is_valid():
            product = product_serializer.save()
            self._save_product_images(request, product)
            return Response(product_serializer.data)
        else:
            return Response(product_serializer.errors)

    def update(self, request, *args, **kwargs):
        product = self.get_object()
        product_serializer = ProductSerializer(product, data=request.data)
        if product_serializer.is_valid():
            product = product_serializer.save()
            self._save_product_images(request, product)
            return Response(product_serializer.data)
        else:
            return Response(product_serializer.errors)

    def _save_product_images(self, request, product):
        images = request.FILES.getlist('images')
        for image in images:
            ProductImage.objects.create(product=product, image=image)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def add_images(self, request, pk=None):
        product = self.get_object()
        self._save_product_images(request, product)
        return Response({'status': 'images uploaded'})

    def list(self, request, *args, **kwargs):
        category_name = request.query_params.get('category')
        if category_name:
            products = Product.objects.filter(category__name=category_name, available=True)
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        return super().list(request, *args, **kwargs)


class AddToCartView(APIView):
    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        user = get_object_or_404(User, profile__telegram_id=telegram_id)
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not item_created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)

        cart_item.total_price = cart_item.quantity * product.price
        cart_item.save()

        return Response({"message": "Товар добавлен в корзину"}, status=status.HTTP_201_CREATED)


class RemoveFromCartView(APIView):
    def delete(self, request, telegram_id, *args, **kwargs):
        cart_item_id = request.data.get('cart_item_id')
        user = get_object_or_404(User, profile__telegram_id=telegram_id)
        cart = get_object_or_404(Cart, user=user)
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
        cart_item.delete()

        return Response({"message": "Товар удален из корзины"}, status=status.HTTP_204_NO_CONTENT)


class CartView(APIView):
    def get(self, request, telegram_id):
        user = get_object_or_404(User, profile__telegram_id=telegram_id)
        cart, created = Cart.objects.get_or_create(user=user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
