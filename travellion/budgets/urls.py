from django.urls import path, include, re_path
from .views import GroupViewSet, PlanViewSet, CategoryViewSet, GroupListSet
from rest_framework.routers import SimpleRouter

group_router = SimpleRouter(trailing_slash=False)
group_router.register('group', GroupViewSet, basename='group')

grouplist_router = SimpleRouter(trailing_slash=False)
grouplist_router.register('grouplist', GroupListSet, basename='grouplist')

plan_router = SimpleRouter(trailing_slash=False)
plan_router.register('plan', PlanViewSet, basename='plan')

category_router = SimpleRouter(trailing_slash=False)
category_router.register('category', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(group_router.urls)),
    re_path(r'^(?P<userId>[0-9a-f-]+)/', include(grouplist_router.urls)),

    re_path(r'^(?P<userId>[0-9a-f-]+)/grouplist/(?P<groupId>\d+)/', include(plan_router.urls)),
    re_path(r'^(?P<userId>[0-9a-f-]+)/grouplist/(?P<groupId>\d+)/plan/(?P<planId>\d+)/', include(category_router.urls)),
]