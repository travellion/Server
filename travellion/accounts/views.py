from django.shortcuts import render
from .serializers import UserSerializer, ProfileSerializer, LoginSerializer# , MyTokenObtainPairSerializer
from .models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.contrib.auth import login, logout, authenticate
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail.message import EmailMessage

class BlacklistRefreshView(APIView):   # 로그아웃시 리프레시 토큰 blacklist
    def post(self, request):
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
        return Response("Success")

class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        #user = User.objects.get(email=request.data['email'])
        user = authenticate(request, email=email, password=password)
       
        if user is not None:
            refresh = RefreshToken.for_user(user)
            serializer = ProfileSerializer(user)
            return Response({
                'userId': serializer.data.get('userId'),
                'email': serializer.data.get('email'),
                'nickname': serializer.data.get('nickname'),
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
class ProfileList(generics.RetrieveUpdateAPIView):

    lookup_field = 'userId'

    queryset = User.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self, **kwargs): # Override
        userId = self.kwargs['userId']
        return self.queryset.filter(userId=userId)
    

def send_email(request):
    subject = "message"
    to = ["id@gmail.com"]
    from_email = "id@gmail.com"
    message = "메시지 테스트"
    EmailMessage(subject=subject, body=message, to=to, from_email=from_email).send()