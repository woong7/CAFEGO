from django import views
from django.core import serializers
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
#from django.contrib.auth.models import User #회원가입을 구현하는데 있어 장고가 제공해주는 편리함
from django.urls import reverse
from django.contrib import auth
from django.views import View
from django.contrib.auth import authenticate, login, logout
from .models import * #User
from cafe.models import CafeList, Review, ReviewPhoto
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from . import forms
from cafe.forms import ReviewForm
from django.contrib import messages
from django.db.models import Q, Count
from datetime import datetime, timedelta
from dateutil import relativedelta

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

def home(request):
    users=User.objects.all()
    cafenum=CafeList.objects.all()
    return render(request,'accounts/home.html',{'cafenum':len(cafenum), 'usernum':len(users)})

def create_admin(request):

    User.objects.create(username="admin", password="pbkdf2_sha256$260000$L95dMuH6iFqEPNxkUzccWw$kVY2VDHFJe4WiywG6HA4/SLbB1wWwHoeJtkxxY7KHRY=", nickname="tester1", is_admin=True)
    return redirect('home')

def badge_list(request, pk):
    user=User.objects.get(id=pk)
    badges=Badge.objects.all()
    jsonDec=json.decoder.JSONDecoder()
    myList=jsonDec.decode(user.badge_taken)
    taken_badges=[]
    for badge in badges:
        if badge.badge_name in myList:
            taken_badges.append(badge)   
    ctx={'badges':badges, 'taken_badges':taken_badges, 'owner':user, 'taken_num':len(taken_badges), 'total_num':len(badges)-2,}

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
    

    ctx={'taken_badges':taken_badges,'user':user,}
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

    ctx={'taken_badges':taken_badges, 'user':user,}
    return render(request, 'accounts/badge_untaken.html', context=ctx)

import math
def user_cafe_map(request):
    visited_cafes = VisitedCafe.objects.all()
    visited_cafe_list = serializers.serialize('json', visited_cafes)

    main_cafe = None
    if len(visited_cafes) >= 0:
        main_cafe = visited_cafes[0]
        for i in range(1, len(visited_cafes)):
            if visited_cafes[i-1].visit_count < visited_cafes[i].visit_count:
                main_cafe = visited_cafes[i]
    
    cafes = CafeList.objects.all().order_by('location_x')
    cafe_list = serializers.serialize('json', cafes)

    ctx = {
        'data': visited_cafe_list,
        'main_cafe': main_cafe.pk,
        'cafe_list': cafe_list
    }
    return render(request, 'accounts/user_cafe_map.html', ctx)

def user_detail(request):
    return render(request, 'accounts/detail.html')

def rank_detail(request):
    return render(request, 'accounts/rank_detail.html')

def rank_list(request):
    now = datetime.today() #오늘
    this_month_first = datetime(now.year, now.month, 1) #오늘을 기준으로 이번달 첫 시간
    next_mnoth_first = this_month_first + relativedelta.relativedelta(months=1)
    this_month_last = next_mnoth_first - timedelta(seconds=1) #오늘을 기준으로 이번달 막 시간

    # print(this_month_first, this_month_last)
    
    ####################  A_총 방문 랭킹  ####################
    A_users=User.objects.all().order_by('-total_visit')
    

    ####################  B_한 달 방문 랭킹  ####################
    B_users=User.objects.all().order_by('-total_visit')



    ####################  C_리뷰 랭킹  ####################
    #annotate를 통해 review_count라는 새로운 필드를 만든다.(모델 속의 필드가 아닌 다른 정렬기준을 새로 만드는 것!)
    #review_count는 Count함수를 이용한 계산 필드
    #review_person은 Review 모델에서 User를 참조하는 username의 related_name이다. 
    #그니까 review_person을 통해 해당 유저의 리뷰를 세고 그 숫자로 정렬
    C_each_users_review = User.objects.all().annotate(review_count = Count('review_person')).order_by('-review_count')
    
    for i in C_each_users_review:
        user_review = i.review_person.all() #<QuerySet [<Review: 1st 3stars>, <Review: 2nd 2stars>, <Review: 3rd 5stars>]>
        C_user_review_count = len(user_review)#리뷰 개수 나옴


    ctx={
        ##### A_총 방문 랭킹 #####
        'A_users':A_users,
        ##### C_리뷰 랭킹 #####
        'C_each_users_review': C_each_users_review,

    }

    return render(request, 'accounts/rank_list.html', context=ctx)

@login_required
def enroll_home(request):
    return render(request, "accounts/enroll_home.html")

class EnrollNewCafeListView(ListView):
    model = VisitedCafe
    paginate_by = 15
    template_name = 'accounts/enroll_new_cafe.html'
    context_object_name = 'new_cafe_list'

    #검색기능
    def get_queryset(self):
        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '') 
        visited_cafe_list = VisitedCafe.objects.filter(user=self.request.user).order_by('-id')
        
        names_to_exclude = [o.cafe for o in visited_cafe_list] 
        new_cafe_list = CafeList.objects.exclude(name__in=names_to_exclude)

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
    #Django Paginator를 사용하여 간단하게 페이징처리를 구현할 수 있지만 
    #하단부의 페이지 숫자 범위를 커스텀하기 위해 
    #get_context_data 메소드로 페이지 숫자 범위 Context를 생성하여 템플릿에 전달한다.
    def get_context_data(self, **kwargs):
        #pk값 얻어옴, *kwargs는 키워드된 n개의 변수들을 함수의 인자로 보낼 때 사용
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        #10번째 버튼?
        page_numbers_range = 10
        #page_range():(1부터 시작하는)페이지 리스트 반환 
        max_index = len(paginator.page_range)

        page = self.request.GET.get('page')
        current_page = int(page) if page else 1

        start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
        end_index = start_index + page_numbers_range
        if end_index >= max_index:
            end_index = max_index

        page_range = paginator.page_range[start_index:end_index]
        context['page_range'] = page_range

        ##
        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '') 

        if len(search_keyword) > 1:
            context['q'] = search_keyword
        context['type'] = search_type

        return context

class EnrollVisitedCafeListView(ListView):
    model = VisitedCafe
    paginate_by = 15
    template_name = 'accounts/enroll_visited_cafe.html'
    context_object_name = 'visited_cafe_list'

    #검색 기능
    def get_queryset(self):
        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '') 
        visited_cafe_list = VisitedCafe.objects.filter(user = self.request.user).order_by('id')#나중에 ㄱㄴㄷ 순으로 바꿀?
        
        names_to_include = [o.cafe for o in visited_cafe_list] 
        cafe_list = CafeList.objects.filter(name__in=names_to_include)
        
        if search_keyword:
            if len(search_keyword) > 1:
                if search_type == 'name':
                    search_cafe_list = cafe_list.filter(name__icontains=search_keyword)
                elif search_type == 'address':
                    search_cafe_list = cafe_list.filter(address__icontains=search_keyword)
                elif search_type == 'all':
                    search_cafe_list = cafe_list.filter(Q(name__icontains=search_keyword) | Q(address__icontains=search_keyword))
                names_to_include = [o.cafe for o in visited_cafe_list] 
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

def mypage(request, pk):
    #내가 방문한 카페들
    visit_cafes=VisitedCafe.objects.filter(user=request.user)
    user=request.user

    jsonDec=json.decoder.JSONDecoder()

    total_drink = []
    total_drink_dic = {}

    for v_cafe in visit_cafes:
        #내가 마신 음료들
        my_drinks = jsonDec.decode(v_cafe.drink_list)
        
        drink_list = []
        for drink in my_drinks:#각 음료들
            #if drink.drinkname not in my_drink:#내가 마신 음료에 없다면
            drink_list.append(drink)

        total_drink.append(drink_list)# 각각에 모든 음료 데이터들이 들어감,,,
        total_drink_dic[v_cafe] = drink_list

    owner=User.objects.get(id=pk)
    print("vcafe:", visit_cafes)
    
    print("total drink:", total_drink)#
    print("total drink dic:", total_drink_dic)#
    print("total drink dic type:", type(total_drink_dic))#

        #drink_list = Drink.objects.get(visited_cafe=cafe)#되나?
    
    #print("drink", drink)
    #print(drink_list.drinkname)
    jsonDec=json.decoder.JSONDecoder()
    badgeList=jsonDec.decode(owner.badge_taken)
    friendsList=jsonDec.decode(owner.friends)

    excludesList=jsonDec.decode(user.friends)
    names_to_exclude = [o for o in excludesList]
    names_to_exclude.append(user.nickname)

    users=User.objects.all()
    friends=[]
    for user in users:
        if user.nickname in friendsList:
            friends.append(user)
        

    my_all_review = Review.objects.filter(username=request.user)
    all_review_count = len(my_all_review)

        
    users=users.order_by('-total_visit')
    
    badgeList=[]

    #배지 획득조건
    if owner.total_visit>=1:
        badgeList.append("카페홀릭")
    if all_review_count>=1:
        badgeList.append("파워블로거")
    if len(friends)>=1:
        badgeList.append("사교왕")
    if len(visit_cafes)>=1:
        badgeList.append("개척자")
    
    if len(users)>=1 and users[0]==owner : 
        badgeList.append("랭킹 1위")
    elif len(users)>=2 and users[1]==owner:
        badgeList.append("랭킹 2위")
    elif len(users)>=3 and users[2]==owner:
        badgeList.append("랭킹 3위")

    badges=Badge.objects.all()
    taken_badges=[]
    for badge in badges:
        if badge.badge_name in badgeList:
            taken_badges.append(badge) 

    total_badge_count = len(taken_badges)

    #user에 총 카페 방문횟수 저장
    owner.badge_taken=json.dumps(badgeList)
    owner.save()
    #print("!!!!", this_user.total_visit)

    ctx={
        'owner':owner,
        'taken_badges':taken_badges,
        'visit_cafes':visit_cafes,
        'friends':friends,
        'drink_list' :total_drink,
        'drink_list_dic' :total_drink_dic,
        'total_visit':owner.total_visit,
        'total_badge_count':total_badge_count,
        'names_to_exclude':names_to_exclude,
        'all_review_count': all_review_count,
    }

    return render(request, 'accounts/mypage.html', context=ctx)

class MyCafeReviewListView(ListView):
    model = Review
    paginate_by = 5
    template_name = 'accounts/myreview_list.html'
    context_object_name = 'my_all_review'

    def get_queryset(self):
        #여기서 위에서 지정한 모델을 필터링하는 것. 어떤 객체를 보낼지 최종적으로 보낸다.
        return Review.objects.filter(username=self.request.user)

    # paginate
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page_numbers_range = 10
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

def review_update(request, pk):
    myreview = get_object_or_404(Review, id=pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=myreview)
        if form.is_valid():
            myreview = form.save(commit=False)
            myreview.username = request.user
            myreview.cafe = CafeList.objects.get(pk=pk)
            myreview = form.save()

        for img in request.FILES.getlist('imgs'):
            photo = ReviewPhoto()
            photo.review = myreview
            photo.review_cafe = myreview.cafe
            photo.image = img
            photo.save()
        
        cafe = CafeList.objects.get(pk=myreview.cafe.id)
        return redirect('cafe:review_list', cafe.id)
    else:
        #instance=myreview: 원래 속에 있던 데이터를 넣은 채 가져다 두기
        form = ReviewForm(instance=myreview)
        cafe_name = CafeList.objects.get(pk=pk)
        reviewer = request.user
        ctx = {'form': form, 'cafe_name': cafe_name, 'reviewer': reviewer}
        return render(request, 'cafe/review_form.html', ctx)

from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def visit_register(request):

    if request.method == 'POST':
        req_post = request.POST
        #print("req_post:", req_post)
        try:
            str_cafename = req_post.__getitem__('cafename')
            str_new_drinkname = req_post.__getitem__('etc')
            str_drinkname = req_post.__getitem__('beverage')

        except:
            print("존재하지 않습니다!")
        
        v_cafe = VisitedCafe()
        v_cafe.user = request.user
        v_cafe.cafe = CafeList.objects.get(name=str_cafename)
        v_cafe.visit_check = True
        v_cafe.visit_count += 1

        drink = Drink()
        drink.visited_cafe = v_cafe
        user = User.objects.get(username=request.user)
        user.total_visit += 1

        jsonDec=json.decoder.JSONDecoder()
        drinkList=jsonDec.decode(v_cafe.drink_list)
        #TODO:에러처리 필요,,,! 기타에 뭐 적으면 선택 못하도록, 선택 하면 기타에 못 적도록.
        if str_new_drinkname != "":#8개 중 선택시 etc에는 항상 빈값이 들어간다. 무조건. 기타를 선택시
            drink.drinkname = str_new_drinkname
            drinkList.append(str_new_drinkname)

        else: # 8개 중 선택시.
            drink.drinkname = str_drinkname
            drinkList.append(str_drinkname)
            
        v_cafe.drink_list=json.dumps(drinkList)

        user.save()
        v_cafe.save()
        drink.save()

    return redirect('enroll_new_cafe')


@csrf_exempt
def visited_register(request):

    if request.method == 'POST':
        req_post = request.POST
        try:
            str_cafename = req_post.__getitem__('cafename')
            str_new_drinkname = req_post.__getitem__('etc')
            str_drinkname = req_post.__getitem__('beverage')
        #print("drinkname:", str_drinkname)
        except:
            print("존재하지 않습니다!")
        user = User.objects.get(username=request.user)
        this_cafe = CafeList.objects.get(name=str_cafename)#전체 카페 중 그 카페
        v_cafe = VisitedCafe.objects.get(cafe=this_cafe, user=request.user)
        
        v_cafe.visit_count += 1
        user.total_visit += 1
        drink = Drink.objects.get(visited_cafe=v_cafe)#이전에 등록된 것 근데 이제 필요없을듯,,,

        jsonDec=json.decoder.JSONDecoder()
        drinkList=jsonDec.decode(v_cafe.drink_list)

        if str_new_drinkname != "":
            drinkList.append(str_new_drinkname)
        else:
            drinkList.append(str_drinkname)
        
        v_cafe.drink_list=json.dumps(drinkList)

        user.save()
        v_cafe.save()
        drink.save()

    return redirect('enroll_visited_cafe')

def addfriend(request, pk):
    user=request.user
    jsonDec=json.decoder.JSONDecoder()
    friendsList=jsonDec.decode(user.friends)
    target=User.objects.get(id=pk)
    friendsList.append(target.nickname)

    user.friends=json.dumps(friendsList)
    user.save()

    return redirect('mypage',pk)

def deletefriend(request, pk):
    user=request.user
    jsonDec=json.decoder.JSONDecoder()
    friendsList=jsonDec.decode(user.friends)
    target=User.objects.get(id=pk)
    friendsList.remove(target.nickname)

    user.friends=json.dumps(friendsList)
    user.save()

    return redirect('mypage',pk)

def friend_search(request):

    return render(request, 'accounts/friend_search')


class FriendSearchListView(ListView):
    model = User
    paginate_by = 15
    template_name = 'accounts/friend_search.html'
    context_object_name = 'user_list'

    #검색기능
    def get_queryset(self):
        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '') 
        user=self.request.user
        jsonDec=json.decoder.JSONDecoder()
        friendsList=jsonDec.decode(user.friends)
        user_list=User.objects.all()
        
        names_to_exclude = [o for o in friendsList]
        names_to_exclude.append(user.nickname)
        user_list = User.objects.exclude(nickname__in=names_to_exclude)
        search_user_list=[]

        if search_keyword:
            if len(search_keyword) > 1:
                if search_type == 'nickname':
                    search_user_list = user_list.filter(nickname__icontains=search_keyword)
                elif search_type == 'town':
                    search_user_list = user_list.filter(town__icontains=search_keyword)
                elif search_type == 'all':
                    search_user_list = user_list.filter(Q(nickname__icontains=search_keyword) | Q(town__icontains=search_keyword))
                return search_user_list
            else:
                messages.error(self.request, '2글자 이상 입력해주세요.')
        return user_list

    #하단부에 페이징 처리
    #Django Paginator를 사용하여 간단하게 페이징처리를 구현할 수 있지만 
    #하단부의 페이지 숫자 범위를 커스텀하기 위해 
    #get_context_data 메소드로 페이지 숫자 범위 Context를 생성하여 템플릿에 전달한다.
    def get_context_data(self, **kwargs):
        #pk값 얻어옴, *kwargs는 키워드된 n개의 변수들을 함수의 인자로 보낼 때 사용
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        #10번째 버튼?
        page_numbers_range = 10
        #page_range():(1부터 시작하는)페이지 리스트 반환 
        max_index = len(paginator.page_range)

        page = self.request.GET.get('page')
        current_page = int(page) if page else 1

        start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
        end_index = start_index + page_numbers_range
        if end_index >= max_index:
            end_index = max_index

        page_range = paginator.page_range[start_index:end_index]
        context['page_range'] = page_range

        ##
        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '') 

        if len(search_keyword) > 1:
            context['q'] = search_keyword
        context['type'] = search_type

        return context

@csrf_exempt
def friend_register(request):

    if request.method == 'POST':
        # 프렌드리스트 해체 및 추가 / 저장
        req_post = request.POST
        str_friendname = req_post.__getitem__('friendname')

        user=request.user

        jsonDec=json.decoder.JSONDecoder()
        friendsList=jsonDec.decode(user.friends)
        friendsList.append(str_friendname)
        user.friends=json.dumps(friendsList)
        user.save()

    return redirect('friend_search')