from django.db import models
from accounts.models import User
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist


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
    group= models.ForeignKey(Group, related_name='plans', on_delete=models.CASCADE) # 해당하는 그룹
    planId = models.AutoField(primary_key=True)
    date = models.DateField(null=True, blank=True)
    nDay = models.IntegerField(default = 0)

    def save(self, *args, **kwargs):
        try:
            latest_plan = Plan.objects.filter(group=self.group).latest('date')
            latest_nDay = Plan.objects.filter(group=self.group).latest('nDay')
        except ObjectDoesNotExist:
            latest_plan = None
            latest_nDay = None

        if not latest_plan:
            self.date = self.group.start_date
            self.nDay = 1
        else:
            self.date = latest_plan.date + timedelta(days=1)
            self.nDay = latest_nDay.nDay + 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.date
    

# 카테고리
class Category(models.Model):
    plan = models.ForeignKey(Plan, related_name='categories', on_delete=models.CASCADE)
    categoryId = models.AutoField(primary_key=True)
    category_title = models.CharField(max_length=128)
    writer = models.ForeignKey(User, related_name='category_writer', on_delete=models.SET_NULL, null=True)
    memo = models.CharField(max_length=128, null=True, blank=True)
    emoji = models.CharField(max_length=5, null=True, blank=True)
    cost = models.IntegerField(default=0)

    def __str__(self):
        return self.category_title
    

# # 멤버만 작업할 수 있도록 권한 부여
# plan_content_type = ContentType.objects.get_for_model(Plan)
# category_content_type = ContentType.objects.get_for_model(Category)

# add_plan_permission = Permission.objects.create(
#     codename='add_plan',
#     name='Can add plan',
#     content_type=plan_content_type,
# )

# add_category_permission = Permission.objects.create(
#     codename='add_category',
#     name='Can add category',
#     content_type=category_content_type,
# )

# group_members = Group.member.all()

# # add_plan_permission과 add_category_permission을 사용자들에게 추가
# for member in group_members:
#     member.user_permissions.add(add_plan_permission, add_category_permission)