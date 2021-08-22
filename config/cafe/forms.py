from django import forms
from django.db.models import fields
from .models import Review

# 리뷰 쓰는 폼
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        exclude = ('username', 'cafe',  'updated_at', 'visit_cafe', 'created_at')