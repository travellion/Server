from django.urls import path, include
from .views import UserCreate, LoginView, ProfileList, send_email
from rest_framework_simplejwt import views as jwt_views
from .views import BlacklistRefreshView, SendVerificationEmailView, VerifyEmailView, WithdrawalView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('signup/', UserCreate.as_view()),
    path('login/', LoginView.as_view()),
    
    path('profile/<uuid:userId>/', ProfileList.as_view()), 

    path('', include('rest_framework.urls')),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', BlacklistRefreshView.as_view(), name="logout"), 

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('send_email/', send_email, name='send_email'),

    path('send_verification_email/', SendVerificationEmailView.as_view(), name='send-verification-email'),
    path('verify_email/', VerifyEmailView.as_view(), name='verify-email'),

    path('withdrawal/', WithdrawalView.as_view(), name='withdrawal')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)