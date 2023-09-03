from django.urls import path, include
from .views import GroupViewSet
from rest_framework.routers import SimpleRouter

group_router = SimpleRouter(trailing_slash=False)
group_router.register('group', GroupViewSet, basename='group')

urlpatterns = [
    path('', include(group_router.urls)),
    path('group/<int:groupId>', include(group_router.urls)),
]