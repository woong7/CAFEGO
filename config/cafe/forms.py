from django import forms
from django.db.models import fields
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['cafe', 'stars', 'content', 'photo', 'created_at', 'updated_at']