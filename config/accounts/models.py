from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser
#user model 커스텀
from typing import Any, Collection, Optional, Set, Tuple, Type, TypeVar, Union
from django.contrib.auth.validators import UnicodeUsernameValidator
from accounts.choices import *
#user.username 원래 있는 이름


#class User(AbstractUser):
#     #username = models.CharField(max_length=20) 내장되어 있음!
#     password = models.CharField(max_length=50)
#     agreement = models.BooleanField(default=False)#null=True 맞나?
#     nickname = models.CharField(max_length=20)
#     district = models.CharField(max_length=10, choices=SEOUL_DISTRICT_CHOICES)
#     town = models.CharField(max_length=20, choices=SEOUL_TOWN_CHOICES)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

class UserManager(BaseUserManager):
    def create_user(self, username, nickname, district, town, agree_terms, agree_marketing,  password=None):
        # if not email:
        #     raise ValueError('Users must have an email address')

        user = self.model(
            username = username,
            nickname = nickname,
            district = district,
            town = town,
            # email=self.normalize_email(email),
            agree_terms=agree_terms,
            agree_marketing=agree_marketing,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, nickname, agree_terms, agree_marketing, password):
        user = self.create_user(
            username,
            #email,
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


class User(AbstractBaseUser):
    username_validator: UnicodeUsernameValidator = ...
    username = models.CharField(max_length=150, unique=True) ##########
    # email = models.EmailField(
    #     verbose_name='email',
    #     max_length=255,
    #     #unique=True,
    # )
    email = models.EmailField(blank=True)
    nickname = models.CharField(max_length=150)
    district = models.CharField(max_length=10, choices=SEOUL_DISTRICT_CHOICES)
    town = models.CharField(max_length=20, choices=SEOUL_TOWN_CHOICES)
    agree_terms = models.BooleanField(default=False)
    agree_marketing = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD ='username'#'email'
    REQUIRED_FIELDS = ['nickname', 'agree_terms', 'agree_marketing'] #'town',

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin