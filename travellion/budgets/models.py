from django.db import models
from accounts.models import User


# 그룹
class Group(models.Model):
    groupId = models.AutoField(primary_key=True)
    leader = models.ForeignKey(User, related_name='group_leader', on_delete=models.CASCADE) # 플랜 생성자(리더)
    member = models.ManyToManyField(User, related_name='group_members', null=True, blank=True) # 플랜에 초대된 사람
    title = models.CharField(max_length=512)
    nation = models.CharField(max_length=512)   # 국가
    location = models.CharField(max_length=512, null=True, blank=True) # 지역
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.IntegerField(default=0)

    def __str__(self):
        return self.title
    

# 플랜 (N일)
class Plan(models.Model):
    group= models.ForeignKey(Group, related_name='group_of_plan', on_delete=models.CASCADE) # 해당하는 그룹
    planId = models.AutoField(primary_key=True) # N일차의 N을 담당 
    title = models.CharField(max_length=128)    
    date = models.DateField(null=True, blank=True)
    day_of_week = models.CharField(max_length=48)
    individual_cost = models.IntegerField(default=0)
    total_cost = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title
    

# 카테고리
class Category(models.Model):
    plan = models.ForeignKey(Plan, related_name='plan_of_category', on_delete=models.CASCADE)
    categoryId = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128)
    # writer = models.ForeignKey(Group.member, related_name='plan_writer', on_delete=models.CASCADE)
    writer = models.ForeignKey(
        User,
        related_name='plan_writer',
        on_delete=models.CASCADE,
        limit_choices_to={'group__member': True}  # 멤버만 작성 가능하도록 필터링 조건 추가
    ) 
    memo = models.CharField(max_length=512, null=True, blank=True)
    emoji = models.CharField(max_length=5, null=True, blank=True)
    cost = models.IntegerField(default=0)

    def __str__(self):
        return self.title