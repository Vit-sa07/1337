from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Category, Product, ProductImage
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)

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