from .models import Group
from accounts.models import User
from .serializers import GroupSerializer
from accounts.serializers import LoginSerializer
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
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
    
    def retrieve(self, request, pk=None, **kwargs):
        groupId = self.kwargs['pk']
        group = get_object_or_404(Group, groupId=groupId)  # groupId로 그룹에 들어옴
        
        if self.request.user.is_authenticated:          # 인증된 User일 경우
            if group.member.filter(userId=request.user.userId).exists():     
                print('이미 가입된 그룹')
                serializer=GroupSerializer(group)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print('처음 가입하는 그룹')
                group.member.add(request.user)
                loginUser = request.user
                
                update_serial=GroupSerializer(loginUser, data=request.data, partial=True)

                if update_serial.is_valid():
                    update_serial.save()
                    serializer=GroupSerializer(group)

                return Response(serializer.data, status=status.HTTP_200_OK)
            
        else:                                                    # 로그인 안했을때
            print('로그인후 이용해주세요')
            serializer=LoginSerializer()
        return Response(serializer.data, status=status.HTTP_401_UNAUTHORIZED)
