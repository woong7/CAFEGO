from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
#from django.contrib.auth.models import User #회원가입을 구현하는데 있어 장고가 제공해주는 편리함
from django.urls import reverse
from django.contrib import auth
from django.views import View
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from . import forms
# Create your views here.

def signup(request):
    if request.method == "POST":
        if request.POST["password1"] == request.POST["password2"]:
            user = User.objects.create_user(
                username=request.POST["username"], password=request.POST["password1"])
            auth.login(request, user)
            print("회원가입 성공!")
            return redirect('/accounts/') #home 페이지 따로 만들어야 댐! url 이름이 home 이어야 댐!
        return render(request, 'accounts/signup.html')
    #실패시 안넘어감
    return render(request, 'accounts/signup.html')




###allauth 써서 필요없을 듯???
class LoginView(View):
    def get(self, request):
        form = forms.LoginForm()
        ctx = {
            "form": form,
        }
        return render(request, "accounts/login.html", ctx)

    def post(self, request):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return render(request, "accounts/home.html")

        return render(request, "accounts/login.html", {"form": form})

##allauth 써서 필요 없나??
@login_required
def logout(request):
    django_logout(request)
    return render(request, "accounts/main.html")

def main(request):
    return render(request, 'accounts/main.html')

@login_required
def home(request):
    #return render(request, 'accounts/home.html')
    return render(request,'accounts/home.html')

def badge_list(request):
    return render(request, 'accounts/badge_list.html')

import simplejson as json
def badge_taken(request):
    
    user=request.user

    jsonDec=json.decoder.JSONDecoder()
    myList=jsonDec.decode(user.visited_cafe)
    

    ctx={}

    return render(request, 'accounts/badge_taken.html', context=ctx)

def badge_untaken(request):
    return render(request, 'accounts/badge_untaken.html')

def user_cafe_map(request):
    return render(request, 'accounts/user_cafe_map.html')

def user_detail(request):
    return render(request, 'accounts/detail.html')

def rank_detail(request):
    return render(request, 'accounts/rank_detail.html')

def rank_list(request):
    users=User.objects.order_by('-total_visit')
    ctx={
        users:'users'
    }
    return render(request, 'accounts/rank_list.html', context=ctx)

@login_required
def enroll_home(request):
    return render(request, "accounts/enroll_home.html")

def enroll_new_cafe(request):
    cafe_list = VisitedCafe.objects.all() #user id 넣어서 그 값만 가져와야 함
    if request.method == 'POST':
        form = forms.VisitedCafeForm(request.POST, request.FILES)

        if form.is_valid():
            ##저장
            cafe = VisitedCafe()
            cafe.user = form.cleaned_data['user']
            cafe.cafename = form.cleaned_data['cafename']
            cafe.visit_count = form.cleaned_data['visit_count']
            cafe.cafe_id = form.cleaned_data['cafe_id']
            cafe.save()
    else:
        form = forms.VisitedCafeForm()
    
    return render(request, 'accounts/enroll_new_cafe.html', {
        'cafe_list': cafe_list,
        'form': form,
    })

def enroll_visited_cafe(request):
    return render(request, "accounts/enroll_visited_cafe.html")
