from django.contrib.auth.models import User
from django.db import models



class Avatar(models.Model):
    src = models.ImageField(upload_to='avatars/')
    alt = models.CharField(max_length=50, default='Avatar image')

class Profile(models.Model):
    fullName = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.PositiveIntegerField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    avatar = models.OneToOneField(Avatar, on_delete=models.CASCADE, blank=True, null=True)
