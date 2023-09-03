from django.shortcuts import render
from .serializers import GroupSerializer
from .models import Group
from rest_framework.viewsets import ModelViewSet

class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer