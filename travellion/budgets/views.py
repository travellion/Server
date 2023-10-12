from .models import Group, Plan, Category
from accounts.models import User
from .serializers import GroupSerializer, PlanSerializer, CategorySerializer
from accounts.serializers import LoginSerializer
from rest_framework.viewsets import ModelViewSet, ViewSet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
import jwt
from travellion.settings import JWT_SECRET_KEY

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

from .permissions import IsGroupMember

import requests
from datetime import datetime

@permission_classes([IsAuthenticated])
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

        serializer.instance.member.add(leader)

        return super().perform_create(serializer)
    
    def retrieve(self, request, pk=None, **kwargs):
        groupId = self.kwargs['pk']
        group = get_object_or_404(Group, groupId=groupId)

        # 현재 로그인한 사용자가 그룹의 멤버인지 확인
        if request.user in group.member.all():
            print('이미 가입된 그룹')
        else:
            print('처음 가입하는 그룹')
            group.member.add(request.user)

        serializer = GroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
class GroupListSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_queryset(self, **kwargs): # Override
        id = self.kwargs['userId']
        return self.queryset.filter(member=id)
    

@permission_classes([IsAuthenticated, IsGroupMember])
class PlanViewSet(ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

    permission_classes = [IsGroupMember]

    def get_queryset(self, **kwargs): # Override
        id = self.kwargs['groupId']
        return self.queryset.filter(group=id)


@permission_classes([IsAuthenticated, IsGroupMember])
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    permission_classes = [IsGroupMember]

    def perform_create(self, serializer):  
        access_token = self.request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        try:
            decoded = jwt.decode(access_token, algorithms=['HS256'], verify=True, key=JWT_SECRET_KEY)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        user_id = decoded['userId']
        writer = User.objects.get(pk=user_id)
        serializer.save(writer=writer)

    def get_queryset(self, **kwargs): # Override
        group_id = self.kwargs['groupId']
        plan_id = self.kwargs['planId']

        queryset = Category.objects.filter(
            plan__group__groupId=group_id,
            plan__planId=plan_id,
        )
        return queryset


class ExchangeViewSet(ViewSet):

    api_key = "APIKEY"
    url="https://www.koreaexim.go.kr/site/program/financial/exchangeJSON"

    def list(self, request):
        current_date = datetime.now().strftime('%Y%m%d')        #오늘날짜 포맷팅
        # 11시 이전이면 전날로 나오게 변경해야함
        
        params = {
        'authkey': self.api_key,
        'searchdate': current_date,
        'data':'AP01'
        }

        response=requests.get(self.url, params=params)
        r_data=response.json()

        if response.status_code == 200:
            exchange_data = response.json()
            return Response(exchange_data)
        else:
            return Response({"error": "Request failed."}, status=400)