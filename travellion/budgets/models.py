from django.db import models
from accounts.models import User
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist
import secrets

# 그룹
class Group(models.Model):
    groupId = models.AutoField(primary_key=True)
    leader = models.ForeignKey(User, related_name='group_leader', on_delete=models.CASCADE) # 플랜 생성자(리더)
    member = models.ManyToManyField(User, related_name='group_members', blank=True) # 플랜에 초대된 사람
    title = models.CharField(max_length=512)
    nation = models.CharField(max_length=512)   # 국가
    location = models.CharField(max_length=512, null=True, blank=True) # 지역
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.IntegerField(default=0)

    invite_code = models.CharField(max_length=32, unique=True, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    editPer = models.BooleanField(default=False, null=True, blank=True)

    def generate_invite_code(self, length=16):
        return secrets.token_urlsafe(length)

    invite_email = models.EmailField(null=True, blank=True)
    invited_emails = models.TextField(null=True, blank=True, help_text="Invited email addresses (comma-separated)")

    def save(self, *args, **kwargs):
        # 초대 코드가 없으면 생성
        if not self.invite_code:
            self.invite_code = self.generate_invite_code()

        super().save(*args, **kwargs)

    def add_invited_email(self, email):
        # 새로운 이메일을 초대 목록에 추가
        if self.invited_emails:
            self.invited_emails += f',{email}'
        else:
            self.invited_emails = email

    def save_invited_email(self, email):
        # 초대 목록을 저장
        self.add_invited_email(email)
        self.save()

    def set_new_leader(self, new_leader):
        self.leader = new_leader
        self.save()

    def set_edit(self, edit_per):
        self.editPer = edit_per
        self.save()

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
        str = f"{self.group.title} - {self.nDay}"
        return str

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
        str = f"{self.plan.group.title} - {self.plan.nDay} - {self.category_title}"
        return str