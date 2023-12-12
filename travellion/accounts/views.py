from django.shortcuts import render
from .serializers import UserSerializer, ProfileSerializer, LoginSerializer, EmailVerificationSerializer, EmailSerializer

from .models import User
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import login, logout, authenticate
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail.message import EmailMessage
from django.core.mail import send_mail
import random
from datetime import datetime

from django.shortcuts import redirect
from json import JSONDecodeError
from django.http import JsonResponse
import requests
import os
from rest_framework import status
from .models import *

from django.utils import timezone
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount

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
        
        current_date = datetime.now()
        formatted_date = current_date.strftime('%y%m%d')

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
    


class SendVerificationEmailView(APIView):
    serializer_class = EmailSerializer
    def post(self, request):
        email = request.data.get('email')
        verification_code = str(random.randint(100000, 999999))
        
        # 이메일 보내기
        subject = '회원가입 인증 코드'
        message = f'회원가입을 완료하려면 다음 코드를 입력하세요: {verification_code}'
        from_email = 'yeohaenggagye@gmail.com'
        recipient_list = [email]
        
        send_mail(subject, message, from_email, recipient_list)
        
        # 데이터베이스에 인증 코드 저장
        # EmailVerification.objects.create(email=email, verification_code=verification_code)
        serializer = EmailVerificationSerializer(data={'email':email, 'verification_code':verification_code})

        if serializer.is_valid():
            serializer.save()
            return Response({'message': '인증 코드를 이메일로 전송했습니다.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       # return Response({'message': '인증 코드를 이메일로 전송했습니다.'}, status=status.HTTP_200_OK)


class VerifyEmailView(APIView):
    serializer_class = EmailVerificationSerializer
    def post(self, request):
        email = request.data.get('email')
        verification_code = request.data.get('verification_code')
        
        try:
            # 데이터베이스에서 저장된 인증 코드 검색
            email_verification = User.objects.get(email=email)
            
            if verification_code == email_verification.verification_code:
                # 인증 코드가 일치하면 사용자를 활성화(회원가입 완료)시킴
                user = User.objects.get(email=email)
                user.is_certified = True
                user.save()
                
                # 이메일 인증 코드를 데이터베이스에서 삭제
                user.verification_code = None
                user.save()
                return Response({'message': '인증이 완료되었습니다.'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': '인증 코드가 올바르지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        except User.DoesNotExist:
            return Response({'message': '인증 코드를 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
    

def send_email(request):
    subject = "message"
    to = ["id@gmail.com"]
    from_email = "id@gmail.com"
    message = "메시지 테스트"
    EmailMessage(subject=subject, body=message, to=to, from_email=from_email).send()


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

    User.objects.create(email=email, verification_code=verification_code)


state = os.environ.get("STATE")
BASE_URL = "http://127.0.0.1:8000"
KAKAO_CALLBACK_URI = BASE_URL + '/kakao/callback/'

#Kakao

def kakao_login(request):
    client_id = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")
    return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code&scope=account_email")

def kakao_callback(request):
    client_id = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")
    code = request.GET.get("code")

    # code로 access token 요청
    token_request = requests.get(f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&code={code}")
    token_response_json = token_request.json()

    error = token_response_json.get("error", None)
    if error is not None:
        raise JSONDecodeError(error)

    access_token = token_response_json.get("access_token")

    # access token으로 카카오톡 프로필 요청
    profile_request = requests.post(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()
    
    error = profile_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    
    kakao_account = profile_json.get("kakao_account")
    email = kakao_account.get("email", None) 
    nickname = kakao_account.get("nickname", None)

    # 이메일 없으면 오류 => 카카오톡 최신 버전에서는 이메일 없이 가입 가능해서 추후 수정해야함
    if email is None:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    
    uid = profile_json.get("id")

    try:
        user = User.objects.get(email=email)
        social_user = SocialAccount.objects.get(user=user)

        if social_user.provider != "kakao":
            return JsonResponse(
                {"err_msg": "no matching social type"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}api/v1/auth/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signin"}, status=accept_status)
        
    except User.DoesNotExist: 
        try:
            user = User.objects.create(email=email,nickname=nickname)
        except:
            nickname = "kakao_" + str(uid)
            user = User.objects.create(email=email,nickname=nickname)

        SocialAccount.objects.create(
            user=user,
            uid=uid,
            extra_data=profile_json,
            date_joined=profile_json.get("connected_at"),
            last_login=timezone.now(),
            provider="kakao",
        )
    except SocialAccount.DoesNotExist:
        return JsonResponse(
            {"err_msg": "user exists but not social user"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = User.objects.get(email=email)
    login(request, user)

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    response_data = {
        "message": "Login Susccess",
        "access_token": access_token,
        "refresh_token": str(refresh),
    }
    response = JsonResponse(response_data)
    return response

    
class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    callback_url = KAKAO_CALLBACK_URI
    client_class = OAuth2Client