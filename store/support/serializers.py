from rest_framework import serializers
from .models import Ticket, Response


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = '__all__'
