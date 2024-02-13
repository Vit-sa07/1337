# views.py в приложении support

from rest_framework import viewsets, status, generics
from rest_framework.response import Response as RestResponse
from .models import Ticket, Response
from .serializers import TicketSerializer, ResponseSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class ResponseCreateView(generics.CreateAPIView):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
