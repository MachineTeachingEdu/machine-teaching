from rest_framework import viewsets
from questions import models
from .serializers  import DropoutRiskSerializer

class DropoutRiskViewSet(viewsets.ModelViewSet):
    queryset = models.DropoutRisk.objects.all()
    serializer_class = DropoutRiskSerializer


