from django import views
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
#from django.contrib.auth.models import User #회원가입을 구현하는데 있어 장고가 제공해주는 편리함
from django.urls import reverse
from django.contrib import auth
from django.views import View
from django.contrib.auth import authenticate, login, logout
from .models import * #User
from cafe.models import CafeList
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from . import forms
from django.contrib import messages
from django.db.models import Q
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
    badges=Badge.objects.all()
    ctx={'badges':badges}

    return render(request, 'accounts/badge_list.html', context=ctx)

import simplejson as json
def badge_taken(request):
    user=request.user

    jsonDec=json.decoder.JSONDecoder()
    myList=jsonDec.decode(user.badge_taken)
    badges=Badge.objects.all()
    taken_badges=[]
    for badge in badges:
        if badge.badge_name in myList:
            taken_badges.append(badge)   
    

    ctx={'taken_badges':taken_badges}
    return render(request, 'accounts/badge_taken.html', context=ctx)

def badge_untaken(request):
    user=request.user

    jsonDec=json.decoder.JSONDecoder()
    myList=jsonDec.decode(user.badge_taken)
    badges=Badge.objects.all()
    taken_badges=[]
    for badge in badges:
        if not badge.badge_name in myList:
            taken_badges.append(badge) 

    ctx={'taken_badges':taken_badges}
    return render(request, 'accounts/badge_untaken.html', context=ctx)

def user_cafe_map(request):
    return render(request, 'accounts/user_cafe_map.html')

def user_detail(request):
    return render(request, 'accounts/detail.html')

def rank_detail(request):
    return render(request, 'accounts/rank_detail.html')

def rank_list(request):
    users=User.objects.all()
    for visit_user in users:
        visit_user.total_visit=0
        visit_cafes=VisitedCafe.objects.filter(user=visit_user)
        for cafe in visit_cafes:
            visit_user.total_visit+=cafe.visit_count
        
    users.order_by('-total_visit')
    ctx={
        'users':users
    }
    return render(request, 'accounts/rank_list.html', context=ctx)

@login_required
def enroll_home(request):
    return render(request, "accounts/enroll_home.html")

class EnrollNewCafeListView(ListView):
    model = VisitedCafe
    paginate_by = 5
    template_name = 'accounts/enroll_new_cafe.html'
    context_object_name = 'new_cafe_list'


    def get_queryset(self):
        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '') 
        visited_cafe_list = VisitedCafe.objects.filter(user=self.request.user)
        names_to_exclude = [o.cafe for o in visited_cafe_list] 
        new_cafe_list = CafeList.objects.exclude(name__in=names_to_exclude).order_by('-id')

        if search_keyword:
            if len(search_keyword) > 1:
                if search_type == 'name':
                    search_cafe_list = new_cafe_list.filter(name__icontains=search_keyword)
                elif search_type == 'address':
                    search_cafe_list = new_cafe_list.filter(address__icontains=search_keyword)
                elif search_type == 'all':
                    search_cafe_list = new_cafe_list.filter(Q(name__icontains=search_keyword) | Q(address__icontains=search_keyword))
                return search_cafe_list
            else:
                messages.error(self.request, '2글자 이상 입력해주세요.')
        return new_cafe_list

    #하단부에 페이징 처리
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page_numbers_range = 5
        max_index = len(paginator.page_range)

        page = self.request.GET.get('page')
        current_page = int(page) if page else 1

        start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
        end_index = start_index + page_numbers_range
        if end_index >= max_index:
            end_index = max_index

        page_range = paginator.page_range[start_index:end_index]
        context['page_range'] = page_range

        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '') 

        if len(search_keyword) > 1:
            context['q'] = search_keyword
        context['type'] = search_type

        return context

class EnrollVisitedCafeListView(ListView):
    model = VisitedCafe
    paginate_by = 5
    template_name = 'accounts/enroll_visited_cafe.html'
    context_object_name = 'visited_cafe_list'

    #검색 기능
    def get_queryset(self):
        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '') 
        visited_cafe_list = VisitedCafe.objects.filter(user=self.request.user).order_by('id')#나중에 ㄱㄴㄷ 순으로 바꿀?

        if search_keyword:
            if len(search_keyword) > 1:
                if search_type == 'name':
                    search_cafe_list = visited_cafe_list.filter(name__icontains=search_keyword)
                elif search_type == 'address':
                    search_cafe_list = visited_cafe_list.filter(address__icontains=search_keyword)
                elif search_type == 'all':
                    search_cafe_list = visited_cafe_list.filter(Q(name__icontains=search_keyword) | Q(address__icontains=search_keyword))
                return search_cafe_list
            else:
                messages.error(self.request, '2글자 이상 입력해주세요.')
        return visited_cafe_list

    #하단부에 페이징 처리
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page_numbers_range = 5
        max_index = len(paginator.page_range)

        page = self.request.GET.get('page')
        current_page = int(page) if page else 1

        start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
        end_index = start_index + page_numbers_range
        if end_index >= max_index:
            end_index = max_index

        page_range = paginator.page_range[start_index:end_index]
        context['page_range'] = page_range

        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '') 

        if len(search_keyword) > 1:
            context['q'] = search_keyword
        context['type'] = search_type

        return context

def mypage(request):

    visit_cafes=VisitedCafe.objects.filter(user=request.user)
    user=request.user

    jsonDec=json.decoder.JSONDecoder()
    myList=jsonDec.decode(user.badge_taken)
    badges=Badge.objects.all()
    taken_badges=[]
    for badge in badges:
        if not badge.badge_name in myList:
            taken_badges.append(badge) 

    ctx={
        'taken_badges':taken_badges,
        'visit_cafes':visit_cafes,
    }

    return render(request, 'accounts/mypage.html', context=ctx)

from django.views.decorators.csrf import csrf_exempt
import json

from django.forms.models import model_to_dict
@csrf_exempt
def visit_register(request):

    if request.method == 'POST':
        req_post = request.POST
        str_cafename = req_post.__getitem__('cafename')
        v_cafe = VisitedCafe()
        v_cafe.user = request.user
        v_cafe.cafe = CafeList.objects.get(name=str_cafename)
        v_cafe.visit_check = True
        v_cafe.visit_count += 1
        v_cafe.save()

    return redirect('enroll_new_cafe')
