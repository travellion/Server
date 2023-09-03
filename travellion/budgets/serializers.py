from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Group

class GroupSerializer(ModelSerializer):
    class Meta:
        model=Group
        fields=['leader', 'member', 'title', 'nation', 'budget', 'start_date', 'end_date']