from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, ResponseCreateView

router = DefaultRouter()
router.register(r'tickets', TicketViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('responses/', ResponseCreateView.as_view(), name='create-response'),
]
