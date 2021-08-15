from django import forms
from django.contrib.auth import get_user_model
from . import models
from .models import Drink, User, VisitedCafe
from allauth.account.forms import SignupForm
from accounts.choices import *

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        try:
            user = models.User.objects.get(username=username)
            if user.check_password(password):
                return self.cleaned_data
            else:
                raise forms.ValidationError("password is wrong!")
        except models.User.DoesNotExist:
            raise forms.ValidationError("user does not exist!")

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

class MyCustomSignupForm(SignupForm):
    agree_terms = forms.BooleanField(label='서비스 이용약관 및 개인정보방침 동의')
    agree_marketing = forms.BooleanField(label='마케팅 이용 동의')
    nickname = forms.CharField(max_length=150, label='닉네임을 입력하세요')

    def save(self, request):
        user = super(MyCustomSignupForm, self).save(request)
        req_post = request.POST
        user.city = req_post.__getitem__('addressRegion')
        user.gu = req_post.__getitem__('addressDo')
        user.dong = req_post.__getitem__('addressSiGunGu')
        user.nickname = self.cleaned_data['nickname']
        user.agree_terms = self.cleaned_data['agree_terms']
        user.agree_marketing = self.cleaned_data['agree_marketing']
        user.save()
        return user

from django.contrib.auth.forms import UserCreationForm
class UserRegistrationForm(UserCreationForm):
    
    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'nickname', 'district', 'town')


class VisitedCafeForm(forms.ModelForm):
    class Meta:
        model = VisitedCafe
        fields = '__all__'

###yeram: drink 모델 choice 바꾸면 적용 아니면 삭제###
class DrinkForm(forms.ModelForm):
    def __init__(self, *args, **kargs):
        super(DrinkForm, self).__init__(*args, **kargs)

    class Meta:
        model = Drink
        exclude = ('visited_cafe', 'created_at', 'updated_at') #
        fields = ['drinkname',]


