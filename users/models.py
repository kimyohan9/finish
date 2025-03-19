from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings

class CustomUser(AbstractUser):
    pass
    # email = models.EmailField(unique=True)  # 이메일 필드
    # preferred_crop = models.CharField(max_length=50)  # 선호 작물 필드

    # def __str__(self):
    #     return self.username
    
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')  # 변경된 부분
    bio = models.TextField(blank=True, null=True)  # 사용자의 소개글
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # 프로필 사진
    location = models.CharField(max_length=100, blank=True, null=True)  # 위치

    def __str__(self):
        return f'{self.user.username} Profile'