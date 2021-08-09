#from config.cafe.models import CafeList
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser
#user model 커스텀
from typing import Any, Collection, Optional, Set, Tuple, Type, TypeVar, Union
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models.deletion import CASCADE
from accounts.choices import *
#user.username 원래 있는 이름
class UserManager(BaseUserManager):
    def create_user(self, username, nickname, district, town, agree_terms, agree_marketing,  password=None):

        user = self.model(
            username = username,
            nickname = nickname,
            district = district,
            town = town,
            agree_terms=agree_terms,
            agree_marketing=agree_marketing,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, nickname, agree_terms, agree_marketing, password):
        user = self.create_user(
            username,
            nickname,
            password=password,
            district="default district",
            town = "default town",
            agree_terms=agree_terms,
            agree_marketing=agree_marketing,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

import simplejson as json
class User(AbstractBaseUser):
    username_validator: UnicodeUsernameValidator = ...
    username = models.CharField(max_length=150, unique=True) ##########
    email = models.EmailField(blank=True)
    nickname = models.CharField(max_length=150)
    district = models.CharField(max_length=10, choices=SEOUL_DISTRICT_CHOICES)
    town = models.CharField(max_length=20, choices=SEOUL_TOWN_CHOICES)
    agree_terms = models.BooleanField(default=False)
    agree_marketing = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    
    total_visit=models.IntegerField(default=0)

    badge_taken=models.TextField(null=True, default=json.dumps([]))
    
    

    objects = UserManager()

    USERNAME_FIELD ='username'
    REQUIRED_FIELDS = ['nickname', 'agree_terms', 'agree_marketing']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

#방문한 한 카페 정보
class VisitedCafe(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    #visited_cafe = models.ForeignKey(CafeList, on_delete=CASCADE)
    visit_count = models.PositiveIntegerField(default=0)
    cafe_id = models.PositiveIntegerField(default=0)


class Badge(models.Model):
    badge_name=models.TextField(max_length=150, unique=True)
    badge_image=models.ImageField()
    
    
    cafename = models.CharField(max_length=100)

    def __str__(self):
        return self.cafename

#방문한 카페에서 먹은 음료 정보 -> 나중에 objects.all로 가져오기
class Drink(models.Model):
    visited_cafe = models.ForeignKey(VisitedCafe, on_delete=CASCADE)
    drinkname = models.CharField(max_length=50, choices=DRINK_CHOICES)

    def __str__(self):
        return self.drinkname


class Badge(models.Model):
    badge_name=models.TextField(max_length=150, unique=True)
    badge_image=models.ImageField()
    
    