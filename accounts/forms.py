from django import forms
from django.contrib.auth import get_user_model
from . import models
from .models import Drink, User, VisitedCafe
from allauth.account.forms import SignupForm
from accounts.choices import *

from django.contrib.auth.forms import UserChangeForm, UserCreationForm

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

class MyCustomForm(forms.ModelForm):

    def save(self, request):
        user = super(MyCustomForm, self).save(request)
        req_post = request.POST
        req_files =request.FILES
        user.city = req_post.__getitem__('city')
        user.gu = req_post.__getitem__('gu')
        user.dong = req_post.__getitem__('dong')
        user.self_intro = req_post.__getitem__('self_intro')
        user.self_image = req_files.__getitem__('self_image')
        user.save()
        return user

    class Meta:
        model = User
        fields = ('self_intro', 'self_image', 'city', 'gu', 'dong')


class UserRegistrationForm(UserCreationForm):
    
    class Meta:
        model = get_user_model()
        fields = ('username', 'self_intro', 'self_image', 'email', 'nickname', 'city', 'gu', 'dong', 'agree_terms', 'agree_marketing')


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


