from django.db import models

# Create your models here.

class BoardData(models.Model):
    title = models.CharField(max_length=300)
    link = models.URLField()
    vegetablename = models.CharField(max_length=30)
    tag = models.TextField()