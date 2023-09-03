from django.db import models
from accounts.models import User


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