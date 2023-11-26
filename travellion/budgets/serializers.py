from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import *
from accounts.models import User
from accounts.serializers import UserInfoSerializer
from datetime import datetime


class GroupSerializer(ModelSerializer):
    
    duration = serializers.SerializerMethodField()
    dday = serializers.SerializerMethodField()
    leader = serializers.ReadOnlyField(source = 'leader.nickname')
    member = UserInfoSerializer(read_only=True, many=True)
    spent_money = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['groupId', 'leader', 'member', 'title', 'nation', 'location', 'start_date', 'end_date', 'duration', 'budget', 'spent_money', 'dday', 'editPer']

    def get_duration(self, obj):
        start_date = obj.start_date
        end_date = obj.end_date
        if start_date and end_date:
            return (end_date - start_date).days
        return None

    def get_dday(self, obj):
        start_date = obj.start_date
        if start_date:
            today = datetime.now().date()
            days_difference = (start_date - today).days
            if days_difference > 0:
                return f"D-{days_difference}일" # D-며칠
            elif days_difference < 0:
                return f"D+{-days_difference}일" # D+며칠
            else:
                return "D-Day"  # 오늘이 start_date랑 같음
        return None

    def get_spent_money(self, obj):
        plans = obj.plans.all()
        if plans:
            try:
                spent_money = plans.aggregate(spent_money=models.Sum('categories__cost'))['spent_money']
                return spent_money if spent_money is not None else 0
            except Exception as e:
                print(f"Error calculating spent_money: {e}")
                return 0
        else:
            return 0
    

class PlanSerializer(ModelSerializer):

    day_of_week = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    individual_cost = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = ['group','planId', 'nDay', 'date', 'day_of_week', 'individual_cost', 'total_cost']

    def get_day_of_week(self, obj):
        date = obj.date
        if date:
            weekday = date.weekday()
            weekdays = ['월', '화', '수', '목', '금', '토', '일']
            return weekdays[weekday]
        return None
    
    def get_total_cost(self, obj):
        categories = obj.categories.all()
        if categories:
            total_cost = categories.aggregate(total_cost=models.Sum('cost'))['total_cost']
            return total_cost if total_cost is not None else 0
        return 0

    def get_individual_cost(self, obj) :
        categories = obj.categories.all()
        total_cost = self.get_total_cost(obj)

        group = obj.group
        if group and categories:
            members_num = group.member.count()
            if members_num and total_cost:
                return round(total_cost / members_num)
        return 0


class CategorySerializer(ModelSerializer):
    writer = serializers.ReadOnlyField(source = 'writer.nickname')

    class Meta:
        model = Category
        fields = ['plan', 'categoryId', 'category_title', 'writer', 'memo', 'emoji', 'cost']

class GroupInviteSerializer(ModelSerializer):
    class Meta:
        model = Group

class InviteMemberSerializer(ModelSerializer):
    #invited_email = serializers.EmailField()

    class Meta:
        model = Group
        fields = ['invite_email']

class JoinMemberSerializer(ModelSerializer):
    entered_invite_code = serializers.CharField()
    class Meta:
        model = Group
        fields = ['entered_invite_code']
        