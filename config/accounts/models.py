from django.db import models
from django.contrib.auth.models import AbstractUser
#user model 커스텀

#user.username 원래 있는 이름
SEOUL_DISTRICT_CHOICES = [
    ('FR', 'Freshman'), #DB에 저장하는 실제 값, display용 이름
    ('JONGNO', '종로구'),
    ('YONGSAN', '용산구'),
    ('SEOUNGDONG', '성동구'),

]

class User(AbstractUser):
    nickname = models.CharField(max_length=20)
    district = models.CharField(max_length=10, choices=SEOUL_DISTRICT_CHOICES)
    #town = 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Blog(models.Model):
    title = models.CharField(max_length= 200)
    pub_date = models.DateField('date published')
    body = models.TextField()

    def __str__(self):
        return self.title

    #보여지는 글자수 줄이는 함수
    def summary(self):
        return self.body[:100] 