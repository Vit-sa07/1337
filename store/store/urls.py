# urls.py основного проекта (например, myproject/urls.py)

from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Sample API",
        default_version='v1',
        description="API documentation for Sample App",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/products/', include('productss.urls')),
    path('api/support/', include('support.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/users/', include('users.urls')),

    # Swagger urls
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
