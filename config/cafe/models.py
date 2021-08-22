from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from accounts.models import User, VisitedCafe

# Create your models here.
class CafeList(models.Model):
    name = models.CharField(verbose_name='카페 이름', max_length=50)
    address = models.CharField(verbose_name='카페 주소', max_length=50) #구, 동
    location_x = models.FloatField(verbose_name='카페 위도', default=0) #위도, 경도
    location_y = models.FloatField(verbose_name='카페 경도', default=0)
    cafe_stars = models.FloatField(verbose_name='카페 별점', default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])

    def __str__(self):
        return self.name

    def to_json(self):
        return {
            "name": self.name,
            "address": self.address,
            "location_x": self.location_x,
            "location_y": self.location_y,
            "cafe_stars": self.cafe_stars,
        }

class Review(models.Model):
    cafe = models.ForeignKey(CafeList, on_delete=models.CASCADE, related_name='this_cafe')
    visit_cafe = models.ForeignKey(VisitedCafe, on_delete=models.CASCADE, related_name='this_cafe')
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_person')
    
    #앞은 DB저장 값, 뒤는 admin이나 폼에서 표시하는 값
    STARS_CHOICES = [
        ('1.0', '⭐'),
        ('2.0', '⭐⭐'),
        ('3.0', '⭐⭐⭐'),
        ('4.0', '⭐⭐⭐⭐'),
        ('5.0', '⭐⭐⭐⭐⭐'),
    ]
    review_stars = models.CharField(verbose_name='리뷰 별점', default='⭐⭐⭐⭐⭐', choices=STARS_CHOICES, max_length=20)
    content = models.TextField(verbose_name='리뷰 내용')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.content

class ReviewPhoto(models.Model):
    review_cafe = models.ForeignKey(CafeList, on_delete=models.CASCADE, related_name='review_cafe')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='this_review')
    image = models.ImageField(verbose_name='리뷰 사진', upload_to = 'static/image/review/%Y/%m/%d', null=True) 


class Comment(models.Model):
    post = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='review_comment')
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_person')
    content = models.TextField(verbose_name='댓글 내용')

    created_at = models.DateTimeField(default=timezone.now) 
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.content

class Map(models.Model):
    emoticon_list = models.ImageField(upload_to = 'static/image/map/%Y/%m/%d')
    level = models.IntegerField()
