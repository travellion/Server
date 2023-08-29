from django.urls import path, include
from .views import UserCreate, LoginView, ProfileList
from rest_framework_simplejwt import views as jwt_views
from .views import BlacklistRefreshView

urlpatterns = [
    path('signup/', UserCreate.as_view()),
    path('login/', LoginView.as_view()),
    
    path('profile/<int:pk>/', ProfileList.as_view()), 

    path('', include('rest_framework.urls')),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', BlacklistRefreshView.as_view(), name="logout"), 
]