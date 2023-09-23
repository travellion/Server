from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework.authtoken.models import Token
import uuid


class UserManager(BaseUserManager):
    # 일반 user 생성
    def create_user(self, email, nickname, age, password=None, profile=None):#  nickname, 
        if not email:
            raise ValueError('must have user email')
        if not nickname:
            raise ValueError('must have user nickname')
        if not age:
            raise ValueError('must have user age')
        user = self.model(
            email = self.normalize_email(email),
            nickname = nickname,
            profile = profile,
            age = age,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    # 관리자 user 생성
    def create_superuser(self, email, nickname, age, password=None):
        user = self.create_user(
            email = email,
            password = password,
            nickname = nickname,
            age = age,
        )
        token = Token.objects.create(user=user)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    userId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(default='', null=False, blank=False, unique=True)
    nickname = models.CharField(default='', max_length=124, null=False, blank=False, unique=False)
    profile = models.ImageField(verbose_name="profile", blank=True, null=True, upload_to='profile_image')
    age = models.IntegerField(null=True, blank=True)
    is_certified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    # User 모델의 필수 field
    is_active = models.BooleanField(default=True)    
    is_admin = models.BooleanField(default=False)
    @property
    def is_superuser(self):
        return self.is_admin

    @property
    def is_staff(self):
       return self.is_admin

    def has_perm(self, perm, obj=None):
       return self.is_admin

    def has_module_perms(self, app_label):
       return self.is_admin

    @is_staff.setter
    def is_staff(self, value):
        self._is_staff = value
    # 헬퍼 클래스 사용
    objects = UserManager()

    # 사용자의 username field는 nickname으로 설정
    USERNAME_FIELD = 'email'
    # 필수로 작성해야하는 field
    REQUIRED_FIELDS = ['nickname', 'age']

    def save(self, *args, **kwargs):
        if not self.userId:
            self.userId = uuid.uuid4()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
    
# class EmailVerification(models.Model):
#     #user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     verification_code = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)
#     email = models.EmailField()