from django.shortcuts import render, redirect
from django.core import serializers
from django.views.generic import ListView
from .models import CafeList, Review, ReviewPhoto, Comment
from accounts.models import User, VisitedCafe, Badge, Notification
from .forms import ReviewForm
from django.contrib import messages
from django.db.models import Q
import json
import csv
import pandas as pd
from cafe.models import CafeList
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

def review_list(request, pk):
    #해당 카페 /<CafeList: 90도씨> 이렇게 나온다
    this_cafe = CafeList.objects.get(pk=pk) 
    cafe_id = this_cafe.id
    #해당 카페 리뷰
    each_reviews = Review.objects.filter(cafe=this_cafe).order_by('-created_at')
    review_photo = ReviewPhoto.objects.filter(review_cafe=this_cafe) 
    comments = Comment.objects.all()
    #print("each_reviews:", each_reviews)
    #print("each_reviews user:", each_reviews.filter(username=request.user))

    user_visited_cafes = VisitedCafe.objects.filter(cafe=this_cafe, user=request.user)
    #방문했는지 체크 -> 리뷰 작성할 수 있음!
    is_visit = False

    for cafe in user_visited_cafes:
        if cafe.cafe == this_cafe:
            is_visit = True
        else:
            pass
        
    #카페 평균 별점 구하기
    if len(each_reviews) == 0: #division zero 에러 피하기
        cafe_stars_avg = 0.0
    else:
        cafe_stars_sum = 0
        for review_star in each_reviews:
            cafe_stars_sum += int(float(review_star.review_stars))
        
        cafe_stars_avg = cafe_stars_sum/len(each_reviews)
        #카페 평균 별점 db에 저장하기
        #this_cafe.cafe_stars.save() 이렇게 모델 필드 하나만 저장 nono
        #this_cafe.save()이렇게 전체 모델로 저장하기
        this_cafe.cafe_stars = cafe_stars_avg
        this_cafe.save()
    
    ctx={
        'this_cafe': this_cafe,
        'cafe_id': cafe_id,
        'each_reviews': each_reviews,
        'review_photo': review_photo,
        'comments': comments,
        'is_visit': is_visit,
    } 

    return render(request, 'cafe/review_list.html', ctx)

import datetime
@csrf_exempt
def comment_write(request):
    req = json.loads(request.body)
    review_id = req['review_id']
    content = req['content']
    review = Review.objects.get(id=review_id)
    user = User.objects.get(username=request.user)
    comment = Comment.objects.create(post=review, username=user, content=content)
    comment.save()
    now = datetime.datetime.now()
    dayOrNight = now.strftime('%p')
    boolDayOrNight = None
    if dayOrNight == 'PM':
        boolDayOrNight = '오후'
    else:
        boolDayOrNight = '오전'   
    timeString = now.strftime('%Y년 %#m월 %#d일 %#I:%M '+boolDayOrNight)

    print("review user name:", review.username)
    notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=review.username, comment=comment)

    return JsonResponse({'review_id':review_id, 'content':content, 'comment_id':comment.id, 'username':user.username, 'comment_time':timeString, 'notification':notification})

@csrf_exempt
def comment_delete(request):
    req = json.loads(request.body)
    comment_id = req['comment_id']
    comment = Comment.objects.get(id=comment_id)
    comment.delete()
    return JsonResponse({'comment_id':comment_id})


def review_create(request, pk):
    if request.method == 'POST':
        #사진 제외한 review 요소들 저장
        form = ReviewForm(request.POST)
        this_cafe = CafeList.objects.get(pk=pk) 
        if form.is_valid():
            myreview = form.save(commit=False)
            myreview.username = request.user
            myreview.cafe = CafeList.objects.get(pk=pk)
            visit_cafes = VisitedCafe.objects.filter(cafe=myreview.cafe)
            get_user_visit_cafe = visit_cafes.get(user=request.user)

            myreview.visit_cafe = get_user_visit_cafe ####

            myreview = form.save()
            user = User.objects.get(username=request.user)
            user.total_review += 1
            user.review_count_lastmonth += 1
            user.save()

        #review_form.html의 name 속성이 imgs인 input 태그에서 받은 파일을 반복문으로 하나씩 가져온다.
        for img in request.FILES.getlist('imgs'):
            #photo 객체 하나 생성
            photo = ReviewPhoto()
            #외래키로 현재 생성한 review의 기본키 참조(지금 다루는 사진의 리뷰와 카페가 어딘지 지정)
            photo.review = myreview
            photo.review_cafe = myreview.cafe
            #imgs에서 가져온 이미지 파일 하나를 저장
            photo.image = img
            #db에 저장
            photo.save()
        
        #해당 리뷰를 쓴 카페 아이디 추출 (해당 카페의 리뷰를 전부 보려고 함)
        cafe = CafeList.objects.get(pk=myreview.cafe.id)
        
        return redirect('cafe:review_list', cafe.id)
    else:
        form = ReviewForm()
        cafe_name = CafeList.objects.get(pk=pk)
        reviewer = request.user
        ctx = {'form': form, 'cafe_name': cafe_name, 'reviewer': reviewer}
        return render(request, 'cafe/review_form.html', ctx)

class CafeListView(ListView):
    model = CafeList
    #리스트 몇줄 표시
    paginate_by = 10
    template_name = 'cafe/cafe_search.html'
    #변수 이름을 바꿈
    context_object_name = 'cafe_list'

    #검색 기능
    def get_queryset(self):
        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '') 
        cafe_list = CafeList.objects.order_by('id')#나중에 ㄱㄴㄷ 순으로 바꿀?
        
        if search_keyword: #검색결과가 있을 때
            if len(search_keyword) > 1:
                if search_type == 'name':
                #__incontains 대소문자 구별 없이 데이터 가져온다.
                    search_cafe_list = cafe_list.filter(name__icontains=search_keyword)
                elif search_type == 'address':
                    search_cafe_list = cafe_list.filter(address__icontains=search_keyword)
                elif search_type == 'all':
                    search_cafe_list = cafe_list.filter(Q(name__icontains=search_keyword) | Q(address__icontains=search_keyword))
                return search_cafe_list
            else:
                messages.error(self.request, '2글자 이상 입력해주세요.')
        return cafe_list

    #하단부에 페이징 처리
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_visited_cafes = VisitedCafe.objects.filter(user=self.request.user)

        user_visit_list = []
        for v_cafe in user_visited_cafes:
            user_visit_list.append(v_cafe.cafe)
        context['user_visited_cafes'] = user_visit_list

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

# 카페 지도
def cafe_map(request):
    cafes = CafeList.objects.all().order_by('location_x')
    cafe_list = serializers.serialize('json', cafes)
    ctx = {
        'data': cafe_list,
    }
    return render(request, 'cafe/cafe_map.html', ctx)

from django.conf import settings
from django.conf.urls.static import static
import os
def init_data(request):
    with open('cafe/crawledminor.csv','r', encoding='utf-8') as f:
        dr = csv.DictReader(f)
        s = pd.DataFrame(dr)
    ss = []
    for i in range(len(s)):
        st = (s['stores'][i], s['X'][i], s['Y'][i],  s['road_address'][i])
        ss.append(st)
    for i in range(len(s)):
        CafeList.objects.create(name=ss[i][0], location_x=ss[i][1], location_y=ss[i][2], address=ss[i][3])

    Badge.objects.create(badge_name="카페홀릭", badge_image="static/image/CafeHolic_badge.png", badge_get="카페 총 누적 방문횟수 X회 이상") 
    Badge.objects.create(badge_name="사교왕", badge_image="static/image/AmericanoLover.png", badge_get="친구 수 X명 이상")    
    Badge.objects.create(badge_name="개척자", badge_image="static/image/CafeHolic_badge.png", badge_get="X개 이상의 카페 방문")    
    Badge.objects.create(badge_name="파워블로거", badge_image="static/image/AmericanoLover.png", badge_get="X개 이상의 리뷰 작성")    
    Badge.objects.create(badge_name="랭킹 1위", badge_image="static/image/금메달.jfif", badge_get="누적 방문 랭킹 1위")    
    Badge.objects.create(badge_name="랭킹 2위", badge_image="static/image/은메달.jfif", badge_get="누적 방문 랭킹 2위")    
    Badge.objects.create(badge_name="랭킹 3위", badge_image="static/image/동메달.jfif", badge_get="누적 방문 랭킹 3위")    

    
    return redirect('home')

def sort_latest(request, pk):
    this_cafe = CafeList.objects.get(pk=pk) 
    each_reviews = Review.objects.filter(cafe=this_cafe).order_by('-created_at')
    review_photo = ReviewPhoto.objects.filter(review_cafe=this_cafe) 
    ctx={'this_cafe': this_cafe, 'each_reviews': each_reviews, 'review_photo': review_photo,
    } 
    return render(request, 'cafe/review_list.html', ctx)

#리뷰를 쓴 유저가 그 카페를 얼마나 방문했는지에 따라서. 내림차순으로.
def sort_visit(request, pk):
    this_cafe = CafeList.objects.get(pk=pk) 
    each_reviews = Review.objects.filter(cafe=this_cafe).order_by('-visit_cafe__visit_count', '-created_at') #해당카페의 리뷰들
    review_photo = ReviewPhoto.objects.filter(review_cafe=this_cafe) 
    ctx={'this_cafe': this_cafe, 'each_reviews': each_reviews, 'review_photo': review_photo,
    } 
    return render(request, 'cafe/review_list.html', ctx)

def sort_total_visit(request, pk):
    this_cafe = CafeList.objects.get(pk=pk) 
    each_reviews = Review.objects.filter(cafe=this_cafe).order_by('-username__total_visit', '-created_at')
    review_photo = ReviewPhoto.objects.filter(review_cafe=this_cafe) 
    ctx={'this_cafe': this_cafe, 'each_reviews': each_reviews, 'review_photo': review_photo,
    } 
    return render(request, 'cafe/review_list.html', ctx)

def sort_review(request, pk):
    this_cafe = CafeList.objects.get(pk=pk) 
    each_reviews = Review.objects.filter(cafe=this_cafe).order_by('-username__total_review', '-created_at')#이름 순으로 정렬
    review_photo = ReviewPhoto.objects.filter(review_cafe=this_cafe) 
    ctx={'this_cafe': this_cafe, 'each_reviews': each_reviews, 'review_photo': review_photo,
    } 
    return render(request, 'cafe/review_list.html', ctx)