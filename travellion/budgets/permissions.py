from rest_framework import permissions
from .models import *

#그룹 멤버 권한
class IsGroupMember(permissions.BasePermission):
    def has_permission(self, request, view):
        group_id = view.kwargs.get('groupId')

        try:
            group = Group.objects.get(pk=group_id)
            is_member = group.member.filter(pk=request.user.pk).exists()
            return is_member
        except Group.DoesNotExist:
            return False
        
#그룹 리더 권한       
class IsGroupLeader(permissions.BasePermission):
    def has_permission(self, request, view):
        group_id = view.kwargs.get('groupId')

        try:
            group = Group.objects.get(pk=group_id)
            if group.editPer:
                return True  # editPer가 True이면 모든 멤버가 권한을 가짐
            else:
                is_leader = group.leader == request.user
                return is_leader
        except Group.DoesNotExist:
            return False