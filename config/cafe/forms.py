from django import forms
from django.db.models import fields
from .models import Review

# 리뷰 쓰는 폼
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['username', 'review_stars', 'content',]


#리뷰 포토 따로 기입 폼
