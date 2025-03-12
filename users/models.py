from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    pass
    # email = models.EmailField(unique=True)  # 이메일 필드
    # preferred_crop = models.CharField(max_length=50)  # 선호 작물 필드

    # def __str__(self):
    #     return self.username