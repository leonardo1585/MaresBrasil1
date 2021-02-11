from django.shortcuts import render
from rest_framework import viewsets
from .models import Lugar
from .serializers import LugarSerializer


class LugarViewSet(viewsets.ModelViewSet):
    queryset = Lugar.objects.all()
    serializer_class = LugarSerializer

def metodo(request):
    return render(request, 'MarApp/index.html')