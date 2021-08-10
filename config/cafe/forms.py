from django import forms
from django.db.models import fields
from .models import Review

# 리뷰 쓰는 폼
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        # fields = ['cafe', 'username', 'review_stars', 'content',] 'created_at',
        exclude = ('username', 'cafe',  'updated_at')
        #cafe_name = forms.CharField(label='cafe_name', max_length=100, required=False) 


#리뷰 포토 따로 기입 폼
