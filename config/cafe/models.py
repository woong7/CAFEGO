from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from accounts.models import User 

# Create your models here.
class CafeList(models.Model):
    name = models.CharField(verbose_name='카페 이름', max_length=50)
    adress = models.CharField(verbose_name='카페 주소', max_length=50) #구, 동
    location_x = models.FloatField(verbose_name='카페 위도', default=0) #위도, 경도
    location_y = models.FloatField(verbose_name='카페 경도', default=0)
    cafe_stars = models.FloatField(verbose_name='카페 별점', default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])

    def __str__(self):
        return self.name


class Review(models.Model):
    cafe = models.ForeignKey(CafeList, on_delete=models.CASCADE, related_name='this_cafe')
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_person')
    STARS_CHOICES = [
        ('1', '⭐'),
        ('2', '⭐⭐'),
        ('3', '⭐⭐⭐'),
        ('4', '⭐⭐⭐⭐'),
        ('5', '⭐⭐⭐⭐⭐'),
    ]
    review_stars = models.CharField(verbose_name='리뷰 별점', default='⭐⭐⭐⭐⭐', choices=STARS_CHOICES, max_length=20)
    content = models.TextField(verbose_name='리뷰 내용')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.content

class ReviewPhoto(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='this_review')
    image = models.ImageField(verbose_name='리뷰 사진', upload_to = 'media/review/%Y/%m/%d', null=True) 


class Comment(models.Model):
    post = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='review_comment')
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_person')
    content = models.TextField(verbose_name='댓글 내용')

    created_at = models.DateTimeField(default=timezone.now) 
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.content

class Map(models.Model):
    emoticon_list = models.ImageField(upload_to = 'media/map/%Y/%m/%d')
    level = models.IntegerField()
