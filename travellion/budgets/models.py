from django.db import models
from accounts.models import User

#대표, 멤버, 제목, 나라, 기간, 예산
class Group(models.Model):
    groupId = models.AutoField(primary_key=True)
    leader = models.ForeignKey(User, related_name='group_leader', on_delete=models.CASCADE)
    member = models.ManyToManyField(User, related_name='group_members')
    title = models.CharField(max_length=512)
    nation = models.CharField(max_length=128)
    budget = models.IntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
 
    def save(self, *args, **kwargs) :
        if self.start_date and self.end_date:
            self.duration = self.end_date - self.start_date
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title