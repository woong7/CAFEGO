from django import views
from django.core import serializers
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView
#from django.contrib.auth.models import User #회원가입을 구현하는데 있어 장고가 제공해주는 편리함
from django.urls import reverse
from django.contrib import auth
from django.views import View
from django.contrib.auth import authenticate, get_user_model, login, logout
from .models import * #User
from cafe.models import CafeList, Review, ReviewPhoto, Comment
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from . import forms
from accounts.forms import UserRegistrationForm, MyCustomSignupForm
from cafe.forms import ReviewForm
from django.contrib import messages
from django.db.models import Q, Count
from datetime import datetime, timedelta
from dateutil import relativedelta
import operator
from django.http import HttpResponseRedirect, HttpResponse

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
        return render(request, "accounts/home.html", ctx)

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
    users = User.objects.all()
    user = request.user
    cafenum=CafeList.objects.all()
    ctx = {
        'cafenum':len(cafenum), 
        'usernum':len(users), 
    }
    if user.is_authenticated:
        ctx['total_visit'] = user.total_visit
    return render(request,'accounts/home.html', ctx)

def create_admin(request):
    User.objects.create(username="admin", password="pbkdf2_sha256$260000$L95dMuH6iFqEPNxkUzccWw$kVY2VDHFJe4WiywG6HA4/SLbB1wWwHoeJtkxxY7KHRY=", nickname="tester1", is_admin=True, is_active=True, city="서울특별시", gu="관악구", dong="신림동")
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

def user_cafe_map(request):
    user = request.user
    visited_cafes = VisitedCafe.objects.filter(user=user)
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
        'nickname': user.nickname,
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
    this_month = now.month-1
    last_month_first = datetime(now.year, now.month-1, 1) #오늘을 기준으로 저번달 첫 시간
    this_month_first = last_month_first + relativedelta.relativedelta(months=1)
    last_month_last = this_month_first - timedelta(seconds=1) #저번달 막 시간
    
    #test용TODO:나중에 지우깅!!
    August = datetime(now.year, now.month, 1)
    September = August + relativedelta.relativedelta(months=1)
    August_fin = September - timedelta(seconds=1)
    
    ####################  A_총 방문 랭킹  ####################
    # A_users=User.objects.all().order_by('-total_visit')
    A_users=User.objects.all().exclude(total_visit=0).order_by('-total_visit')
    A_me=User.objects.get(username=request.user)

    #사용자 리스트에 내가 있으면
    if A_me in A_users:
        #enumerate: 배열의 인덱스와 값을 뽑아내기
        for grade, who in enumerate(A_users):
            if A_me == who:
                A_my_grade = grade + 1 #인덱스는 0,1,2니까 등수 구하려면 +1
    #사용자 리스트가 내가 없으면
    else:
        A_my_grade = 0
    
    ####################  B_한 달 방문 랭킹  ####################
    # B_users=User.objects.all().order_by('-visit_count_lastmonth')
    B_users=User.objects.all().exclude(visit_count_lastmonth=0).order_by('-visit_count_lastmonth')
    B_me=User.objects.get(username=request.user)

    if B_me in B_users:
        for grade, who in enumerate(B_users):
            if B_me == who:
                B_my_grade = grade + 1 
    else:
        B_my_grade = 0

    ####################  C_한 달 카페 종류 랭킹  ####################
    C_monthly_visited_cafe = VisitedCafe.objects.filter(updated_at__date__range=(datetime.date(August), datetime.date(August_fin)))
    C_monthly_kinds_dict = {}
    for i in C_monthly_visited_cafe:
        if i.user not in C_monthly_kinds_dict.keys():#키 리스트
            C_monthly_kinds_dict[i.user.nickname] = [i.cafe]
        else:
            C_monthly_kinds_dict[i.user.nickname].append(i.cafe)
    #여기까지 {user이름:[카페리스트]}이렇게 내가 원하는 대로 나옴!!

    # 카페 종류 **개수**를 넣어주기
    for i in C_monthly_kinds_dict:
        y = len(C_monthly_kinds_dict.get(i))
        C_monthly_kinds_dict[i] = y
        # {<User: ye1>: 3, <User: ye2>: 1}

    #value 값 기준으로 내림차순 정렬
    #[(<User: ye1>, 3), (<User: ye2>, 1)] 이렇게 튜플로 나옴.
    C_monthly_kinds_tuple = sorted(C_monthly_kinds_dict.items(), key=lambda x: x[1], reverse=True)
    #튜플 딕셔너리로 바꿈
    C_monthly_kinds_order = dict(C_monthly_kinds_tuple)

    C_me=User.objects.get(username=request.user)

    if C_me.nickname in C_monthly_kinds_order.keys():
        for grade, who in enumerate(C_monthly_kinds_order.keys()):
            if C_me.nickname == who:
                C_my_grade = grade + 1
    else:
        C_my_grade = 0
    
    ####################  D_누적 리뷰 랭킹  ####################
    D_all_review_order = User.objects.all().order_by('-total_review')#누적 리뷰 랭킹
    D_me=User.objects.get(username=request.user)

    if D_me in D_all_review_order:
        for grade, who in enumerate(D_all_review_order):
            if D_me == who:
                D_my_grade = grade + 1 
    else:
        D_my_grade = 0

    ####################  E_한 달 리뷰 랭킹  ####################
    E_month_review_order = User.objects.all().order_by('-review_count_lastmonth')
    E_me=User.objects.get(username=request.user)

    if E_me in E_month_review_order:
        for grade, who in enumerate(E_month_review_order):
            if E_me == who:
                E_my_grade = grade + 1 
    else:
        E_my_grade = 0

    ctx={
        'last_month_first': last_month_first,
        'last_month_last': last_month_last,
        'this_month': this_month,
        ##### A_총 방문 랭킹 #####
        'A_users': A_users,
        'A_my_grade': A_my_grade,
        ##### B_한 달 방문 랭킹 #####
        'B_users': B_users,
        'B_my_grade': B_my_grade,
        #####  C_한 달 카페 종류 랭킹  #####
        'C_monthly_kinds_order': C_monthly_kinds_order,
        'C_my_grade': C_my_grade,
        # 'C_my_grade': C_my_grade,
        #####  D_누적 리뷰 랭킹  #####
        'D_all_review_order': D_all_review_order,
        'D_my_grade': D_my_grade,
        ##### E_한 달 리뷰 랭킹 #####
        'E_month_review_order' : E_month_review_order,
        'E_my_grade': E_my_grade,
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
                cafes_to_include = [o for o in search_cafe_list] 
                return VisitedCafe.objects.filter(cafe__in=cafes_to_include)
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
    
    user=request.user
    owner=User.objects.get(id=pk)
    visit_cafes=VisitedCafe.objects.filter(user=owner)

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

    
    #print("vcafe:", visit_cafes)
    
    #print("total drink:", total_drink)#
    #print("total drink dic:", total_drink_dic)#
    #print("total drink dic type:", type(total_drink_dic))#

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
        

    my_all_review = Review.objects.filter(username=owner)
    all_review_count = len(my_all_review)
    review_photo = ReviewPhoto.objects.all() 
    comments=Comment.objects.filter(username=owner)

        
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
        'total_visit': owner.total_visit,
        'total_badge_count':total_badge_count,
        'names_to_exclude':names_to_exclude,
        'all_review_count': all_review_count,
        'my_all_review':my_all_review,
        'review_photo':review_photo,
        'comments':comments,
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
            myreview.cafe = CafeList.objects.get(name=myreview.cafe)
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
        if request.user == myreview.username: #리뷰 작성자=사용자
            #instance=myreview: 원래 속에 있던 데이터를 넣은 채 가져다 두기
            form = ReviewForm(instance=myreview)
            cafe_name = CafeList.objects.get(name=myreview.cafe)
            reviewer = request.user
            ctx = {'form': form, 'cafe_name': cafe_name, 'reviewer': reviewer}
            return render(request, 'cafe/review_form.html', ctx)
        else:
            cafe = CafeList.objects.get(pk=myreview.cafe.id)
            ctx = {'cafe': cafe,}
            return render(request, 'cafe/warning.html', ctx)

from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def visit_register(request):
    if request.method == 'POST':
        req_post = request.POST
        #음료 내용 받아온다.
        try:
            str_cafename = req_post.__getitem__('cafename')
            str_new_drinkname = req_post.__getitem__('etc')
            str_drinkname = req_post.__getitem__('beverage')
        except:
            print("존재하지 않습니다!")
        
        #카페를 방문한 유저와 그 유저의 방문 횟수 +1
        v_cafe = VisitedCafe()
        v_cafe.user = request.user
        v_cafe.cafe = CafeList.objects.get(name=str_cafename)
        v_cafe.visit_check = True
        v_cafe.visit_count += 1

        #음료를 저장할 카페, 날짜 저장
        now = datetime.today() ##@@
        drink = Drink()
        drink.visited_cafe = v_cafe
        # v_cafe.created_at = now ##@@
        # print('!!!!!!!', v_cafe.created_at) ##@@
        user = User.objects.get(username=request.user)
        user.total_visit += 1

        #새로운 카페 등록은 무조건 새로운 종류니까 바로 카운트 올림
        user.kinds_of_cafe_lastmonth += 1

        #모달창에서 선택한 음료 저장
        jsonDec=json.decoder.JSONDecoder()
        drinkList=jsonDec.decode(v_cafe.drink_list)
        #TODO:에러처리 필요,,,! 기타에 뭐 적으면 선택 못하도록, 선택 하면 기타에 못 적도록.
        if str_new_drinkname != "":#8개 중 선택시 etc에는 항상 빈값이 들어간다. 무조건. 기타를 선택시
            drink.drinkname = str_new_drinkname
            drinkList.append(str_new_drinkname)
            user.visit_count_lastmonth += 1 

        else: # 8개 중 선택시.
            drink.drinkname = str_drinkname
            drinkList.append(str_drinkname)
            user.visit_count_lastmonth += 1 
            
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
            user.visit_count_lastmonth += 1 
        else:
            drinkList.append(str_drinkname)
            user.visit_count_lastmonth += 1 
        
        v_cafe.drink_list=json.dumps(drinkList)

        #TODO: 문제상황: 1달이 지나 내가 방문했던 카페 종류를 리셋해도 방문한 카페 종류는 리셋이 안됨. 그래서 7월에 방문했던 카페이면 8월에 뭐 어케 추가하냐
        #요약: 시간 무조건 써야하는 것 같음..어렵네
        # #만약 지금 등록하는 카페가 이전에 방문했던 카페가 아니면 카페 종류에 +1
        # #나중에 kinds_of_cafe_lastmonth을 0으로 리셋해도 방문했던 카페가 0이 되는 것은 아니므로
        # #조건문이 필요할 듯..
        # user_v_cafelist = user.visitedcafe_set.all() #class name으로 불러오기(대문자는 모두 소문자로)
        # for i in user_v_cafelist:
        #     if v_cafe.cafe is not i.cafe:
        #         user.kinds_of_cafe_lastmonth += 1

        now = datetime.today()
        # v_cafe.updated_at = now ##@@2021-08-14 11:14:20.326741
        print(v_cafe.updated_at)

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
    notification = Notification.objects.create(notification_type=3, from_user=request.user, to_user=target)
    notification.save()

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

        target =User.objects.get(nickname=str_friendname)
        print("target:", target) #user objects가 맞는지
        notification = Notification.objects.create(notification_type=3, from_user=request.user, to_user=target)
        notification.save()

    return redirect('friend_search')

def this_cafe_map(request, pk):
    cafe = CafeList.objects.get(pk=pk)
    #cafes = CafeList.objects.all().order_by('location_x')
    #cafe_list = serializers.serialize('json', cafes)
    ctx = {
        #'data': cafe_list,
        'cafe_id': cafe.id,
        'cafe_name': cafe.name,
        'cafe_x':cafe.location_x,
        'cafe_y':cafe.location_y,
        'cafe_address':cafe.address,
    }
    return render(request, 'accounts/cafe_map.html', ctx)

##알림 기능
class CommentNotification(View):
    def get(self, request, notification_pk, review_pk, *args, **kwargs):
        # print("self:", self)
        # print("request:", request)
        # print("notification pk:", notification_pk)
        # print("self request get:", self.args)
        # print("self request get:", self.kwargs['review_pk'])
        # print("review_pk:", review_pk)
        notification = Notification.objects.get(pk=notification_pk)
        #체크 필요!!!

        comment = Comment.objects.get(pk=review_pk)
        #comment가 속해잇는 리뷰 객체  리뷰는 또 카페 디테일 페이지
        comment.post #review 객체임
        #해당하는 카페 객체도 받아와야 함!
        this_cafe = comment.post.cafe #cafelist 객체임
        cafe_id = this_cafe.id
        each_reviews = Review.objects.filter(cafe=this_cafe).order_by('-created_at')
        review_photo = ReviewPhoto.objects.filter(review_cafe=this_cafe) 
        comments = Comment.objects.all()
        user_visited_cafes = VisitedCafe.objects.filter(cafe=this_cafe, user=request.user)
            #방문했는지 체크 -> 리뷰 작성할 수 있음!
        is_visit = False

        for cafe in user_visited_cafes:
            if cafe.cafe == this_cafe:
                is_visit = True
            else:
                pass

        print("review??:", comment.post)##???
        print("review pk??:", comment.post.pk)###???
        notification.user_has_seen = True
        notification.save()

        #!!!

        ctx={
        'this_cafe': this_cafe,
        'cafe_id': cafe_id,
        'each_reviews': each_reviews,
        'review_photo': review_photo,
        'comments': comments,
        'is_visit': is_visit,
        } 
        return render(request, 'cafe/review_list.html', ctx)
        #return redirect('review_list', pk=comment.post.pk)#comment pk가 아니라 review pk로,,,!!

class FollowNotification(View):
    def get(self, request, notification_pk, user_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        #체크 필요!
        user = User.objects.get(pk=user_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('mypage', pk=user_pk)

class RemoveNotification(View):
    def delete(self, request, notification_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)

        notification.user_has_seen = True
        notification.save()

        return HttpResponse('Success', content_type='text/plain') #????


from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

class UserRegistrationView(CreateView):
    model = get_user_model()
    form_class = UserRegistrationForm
    success_url = '/home/'
    verify_url = '/verify/' 
    token_generator = default_token_generator

    def form_valid(self, form):
        response = super().form_valid(form) 
        if form.instance:
            self.send_verification_email(form.instance)
        return response

    def send_verification_email(self, user):
        token = self.token_generator.make_token(user)
        send_email_confirmation(self.request, user, email=user.email)
        # user.email_user('회원가입을 축하드립니다.', '다음 주소로 이동하셔서 인증하세요. {}'.format(self.build_verification_link(user, token)), from_email=settings.EMAIL_HOST_USER)
        messages.info(self.request, '회원가입을 축하드립니다. 가입하신 이메일주소로 인증메일을 발송했으니 확인 후 인증해주세요.')

    def build_verification_link(self, user, token):
        return '{}/{}/verify/{}/'.format(self.request.META.get('HTTP_ORIGIN'), user.pk, token)

from django.views.generic.base import TemplateView
class UserVerificationView(TemplateView):
    
    model = get_user_model()
    redirect_url = '/home/'
    token_generator = default_token_generator

    def get(self, request, *args, **kwargs):
        if self.is_valid_token(**kwargs):
            messages.info(request, '인증이 완료되었습니다.')
        else:
            messages.error(request, '인증이 실패되었습니다.')
        return HttpResponseRedirect(self.redirect_url)   # 인증 성공여부와 상관없이 무조건 로그인 페이지로 이동

    def is_valid_token(self, **kwargs):
        pk = kwargs.get('pk')
        token = kwargs.get('tonen')
        user = self.model.objects.get(pk=pk)
        is_valid = self.token_generator.check_token(user, token)
        if is_valid:
            user.is_active = True
            user.save()     # 데이터가 변경되면 반드시 save() 메소드 호출
        return is_valid