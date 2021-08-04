from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from user.models import User 

# Create your models here.
class CafeList(models.Model):
    name = models.CharField(max_length=50)
    adress = models.CharField(max_length=50) #구, 동
    location_x = models.FloatField(default=0) #위도, 경도
    location_y = models.FloatField(default=0)
    stars = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])

    def __str__(self):
        return self.name


class Review(models.Model):
    cafe = models.ForeignKey(CafeList, on_delete=models.CASCADE, related_name='cafe_review')
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_person')
    photo = models.ImageField(upload_to = 'media/review/%Y/%m/%d') 
    STARS_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]
    stars = models.CharField(default='⭐⭐⭐⭐⭐', choices=STARS_CHOICES)
    content = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

class Comment(models.Model):
    post = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='review_comment')
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_person')
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

class Map(models.Model):
    emoticon_list = models.ImageField(upload_to = 'media/map/%Y/%m/%d')
    level = models.IntegerField()
