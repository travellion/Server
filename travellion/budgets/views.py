from django.shortcuts import render
from .serializers import GroupSerializer
from .models import Group
from accounts.models import User
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import AuthenticationFailed
import jwt
from travellion.settings import JWT_SECRET_KEY

class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def perform_create(self, serializer):
        access_token = self.request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        try:
            decoded = jwt.decode(access_token, algorithms=['HS256'], verify=True, key=JWT_SECRET_KEY)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        user_id = decoded['userId']
        leader = User.objects.get(pk=user_id)
        serializer.save(leader=leader)
        return super().perform_create(serializer)
