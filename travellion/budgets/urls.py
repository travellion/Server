from django.urls import path, include, re_path
from .views import GroupViewSet, PlanViewSet, CategoryViewSet, GroupListSet, ExchangeViewSet, InviteMembersAPIView, JoinGroupAPIView, InviteMembersAPIView
from rest_framework.routers import SimpleRouter, DefaultRouter


group_router = SimpleRouter(trailing_slash=False)
group_router.register('group', GroupViewSet, basename='group')

#그룹리더 변경URL
urlpatterns = [
    path('group/<int:group_id>/set_leader/', GroupViewSet.as_view({'post': 'set_leader'}), name='set_group_leader'),
    path('group/<int:group_id>/change_edit_permission/', GroupViewSet.as_view({'post': 'set_edit'}), name='set_edit_permission'),
]

grouplist_router = SimpleRouter(trailing_slash=False)
grouplist_router.register('grouplist', GroupListSet, basename='grouplist')

plan_router = SimpleRouter(trailing_slash=False)
plan_router.register('plan', PlanViewSet, basename='plan')

category_router = SimpleRouter(trailing_slash=False)
category_router.register('category', CategoryViewSet, basename='category')

api_router = SimpleRouter(trailing_slash=False)
api_router.register('exchanges', ExchangeViewSet, basename='api')

urlpatterns = [
    #그룹생성,조회URL
    path('', include(group_router.urls)),
    re_path(r'^(?P<userId>[0-9a-f-]+)/', include(grouplist_router.urls)),

    re_path(r'^(?P<userId>[0-9a-f-]+)/grouplist/(?P<groupId>\d+)/', include(plan_router.urls)),
    re_path(r'^(?P<userId>[0-9a-f-]+)/grouplist/(?P<groupId>\d+)/plan/(?P<planId>\d+)/', include(category_router.urls)),

    #그룹초대URL
    path('join/<int:group_id>/', JoinGroupAPIView.as_view(), name='join_group'),
    path('groups/<int:group_id>/invite/', InviteMembersAPIView.as_view(), name='invite_member'),

    #환율URL
    path('', include(api_router.urls)),
]