from django.shortcuts import render
from .serializers import UserSerializer, ProfileSerializer, LoginSerializer, EmailVerificationSerializer, EmailSerializer

from .models import User, EmailVerification
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.contrib.auth import login, logout, authenticate
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail.message import EmailMessage
from django.core.mail import send_mail
import random
from rest_framework.permissions import IsAuthenticated

class BlacklistRefreshView(APIView):   # 로그아웃시 리프레시 토큰 blacklist
    def post(self, request):
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
        return Response("Success")

class UserCreate(generics.CreateAPIView):
    #if User.is_certified == True:
        queryset = User.objects.all()
        serializer_class = UserSerializer


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
       
        if user is not None:
            refresh = RefreshToken.for_user(user)
            serializer = ProfileSerializer(user)
            return Response({
                'userId': serializer.data.get('userId'),
                'email': serializer.data.get('email'),
                'nickname': serializer.data.get('nickname'),
                'age': serializer.data.get('age'),
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class WithdrawalView(APIView):
    def delete(self, request):
        user = User.objects.get(userId=request.user.userId)
        if user:
            user.delete()
            return Response({"message": "회원탈퇴 성공"}, status=status.HTTP_200_OK)
        return Response({"message": "회원탈퇴 실패"}, status=status.HTTP_400_BAD_REQUEST)


class ProfileList(generics.RetrieveUpdateAPIView):

    lookup_field = 'userId'

    queryset = User.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self, **kwargs): # Override
        userId = self.kwargs['userId']
        return self.queryset.filter(userId=userId)
    


# class SendVerificationEmailView(APIView):
#     serializer_class = EmailSerializer
#     def post(self, request):
#         email = request.data.get('email')
#         verification_code = str(random.randint(100000, 999999))
        
#         # 이메일 보내기
#         subject = '회원가입 인증 코드'
#         message = f'회원가입을 완료하려면 다음 코드를 입력하세요: {verification_code}'
#         from_email = 'yeohaenggagye@gmail.com'
#         recipient_list = [email]
        
#         send_mail(subject, message, from_email, recipient_list)
        
#         # 데이터베이스에 인증 코드 저장
#         # EmailVerification.objects.create(email=email, verification_code=verification_code)
#         serializer = EmailVerificationSerializer(data={'email':email, 'verification_code':verification_code})

#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message': '인증 코드를 이메일로 전송했습니다.'}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#        # return Response({'message': '인증 코드를 이메일로 전송했습니다.'}, status=status.HTTP_200_OK)


# class VerifyEmailView(APIView):
#     serializer_class = EmailVerificationSerializer
#     def post(self, request):
#         email = request.data.get('email')
#         verification_code = request.data.get('verification_code')
        
#         try:
#             # 데이터베이스에서 저장된 인증 코드 검색
#             email_verification = EmailVerification.objects.get(email=email)
            
#             if verification_code == email_verification.verification_code:
#                 # 인증 코드가 일치하면 사용자를 활성화(회원가입 완료)시킴
#                 user = User.objects.get(email=email)
#                 user.is_certified = True
#                 user.save()
                
#                 # 이메일 인증 코드를 데이터베이스에서 삭제
#                 email_verification.delete()
                
#                 return Response({'message': '인증이 완료되었습니다.'}, status=status.HTTP_201_CREATED)
#             else:
#                 return Response({'message': '인증 코드가 올바르지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
#         except EmailVerification.DoesNotExist:
#             return Response({'message': '인증 코드를 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
    

def send_email(request):
    subject = "message"
    to = ["id@gmail.com"]
    from_email = "id@gmail.com"
    message = "메시지 테스트"
    EmailMessage(subject=subject, body=message, to=to, from_email=from_email).send()

# def send_verification_email(email, verification_code):
#     subject = '인증번호 발송'  # 이메일 제목
#     message = f'인증번호: {verification_code}'  # 이메일 내용
#     from_email = 'yeohaenggagye@gmail.com'  # 발신 이메일 주소
#     recipient_list = [email]  # 수신자 이메일 주소 리스트

#     send_mail(subject, message, from_email, recipient_list)

# 회원가입 요청을 받았을 때 이메일 보내기
def send_verification_email(email):
    # 무작위 인증 번호 생성
    verification_code = str(random.randint(100000, 999999))
    
    # 이메일 보내기
    subject = '회원가입 인증 코드'
    message = f'회원가입을 완료하려면 다음 코드를 입력하세요: {verification_code}'
    from_email = 'yeohaenggagye@gmail.com'
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list)

    EmailVerification.objects.create(email=email, verification_code=verification_code)

