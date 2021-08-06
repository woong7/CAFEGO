from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser
#user model 커스텀
from typing import Any, Collection, Optional, Set, Tuple, Type, TypeVar, Union
from django.contrib.auth.validators import UnicodeUsernameValidator
#user.username 원래 있는 이름
SEOUL_DISTRICT_CHOICES = [
    #('FR', 'Freshman'), #DB에 저장하는 실제 값, display용 이름
    ('JONGNO', '종로구'), #이걸 동이랑 어떻게 연결??
    ('YONGSAN', '용산구'),
    ('SEOUNGDONG', '성동구'),
    ('GWANGJIN', '광진구'),
    ('DONGDAEMUN', '동대문구'),
    ('JUNGNANG', '중랑구'),
    ('SEONGBUK', '성북구'),
    ('GANGBUK', '강북구'),
    ('DOBONG', '도봉구'),
    ('NOWON', '노원구'),
    ('EUNPYEONG', '은평구'),
    ('SEODAEMUN', '서대문구'),
    ('MAPO', '마포구'),
    ('YANGCHEON', '양천구'),
    ('GANGSEO', '강서구'),
    #{'종로구': {'1동', '2동', '3동'}},

]

SEOUL_TOWN_CHOICES = [
    ('CHEONGUN', '청운효자동'),
    ('SAJIK', '사직동'),
    ('SAMCHEONG', '삼청동'),
    ('BUAM', '부암동'),
    ('PYEONGCHANG', '평창동'),
    ('MUAK', '무악동'),

]

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
    def create_user(self, username, nickname, agree_terms, agree_marketing,  password=None):
        # if not email:
        #     raise ValueError('Users must have an email address')

        user = self.model(
            username = username,
            nickname = nickname,
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
    agree_terms = models.BooleanField(default=False)
    agree_marketing = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD ='username'#'email'
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