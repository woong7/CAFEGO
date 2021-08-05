from django.db import models
from django.contrib.auth.models import AbstractUser
#user model 커스텀

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

]

SEOUL_TOWN_CHOICES = [
    ('CHEONGUN', '청운효자동'),
    ('SAJIK', '사직동'),
    ('SAMCHEONG', '삼청동'),
    ('BUAM', '부암동'),
    ('PYEONGCHANG', '평창동'),
    ('MUAK', '무악동'),

]

class User(AbstractUser):
    #username = models.CharField(max_length=20) 내장되어 있음!
    password = models.CharField(max_length=50)
    agreement = models.BooleanField(default=False)#null=True 맞나?
    nickname = models.CharField(max_length=20)
    district = models.CharField(max_length=10, choices=SEOUL_DISTRICT_CHOICES)
    town = models.CharField(max_length=20, choices=SEOUL_TOWN_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
