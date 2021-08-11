from django.shortcuts import render, redirect
from django.core import serializers
from django.views.generic import ListView
from .models import CafeList, Review, ReviewPhoto, Comment
from accounts.models import User
from .forms import ReviewForm
from django.contrib import messages
from django.db.models import Q
import json
import csv
import pandas as pd
from cafe.models import CafeList

# Create your views here.
def review_list(request, pk):
    this_cafe = CafeList.objects.get(pk=pk) #해당 카페 /<CafeList: 90도씨> 이렇게 나오지
    each_reviews = Review.objects.filter(cafe=this_cafe) #해당 카페 리뷰/ <QuerySet [<Review: 3>, <Review: 두번째 리뷰 내용>]> 리뷰내용만 출력됨...
    review_photo = ReviewPhoto.objects.filter(review_cafe=this_cafe) #해당 카페 리뷰의 모든 사진(템플릿에서 분류)
    

    print('!!!!1')
    print(this_cafe.cafe_stars)

    if len(each_reviews) == 0:
        cafe_stars_avg = 0.0
    else:
        cafe_stars_sum = 0
        for review_star in each_reviews:
            cafe_stars_sum += int(float(review_star.review_stars))
        
        cafe_stars_avg = cafe_stars_sum/len(each_reviews)
    
    this_cafe.cafe_stars = cafe_stars_avg
    print(this_cafe.cafe_stars)
    # this_cafe.cafe_stars.save()


    #뭐 이거 일단 평균 구하려는 시도임
    # star_sum = 0
    # for i in each_reviews:
    #     #one_review = id
    #     review_star = i.review_stars
    #     star_sum += review_star
    # star_avg = star_sum / len(each_reviews)

    #all_stars = Review.objects.all()
    #all_stars = each_reviews.review_stars #리뷰가 많으니까 가져오질 못함..
    
    # cafe_stars = 0.0
    # for j in all_stars:
    #     if j == '⭐':
    #         j = 1.0
    #         cafe_stars + j / 


    #카페 자체의 별점(초기에 야매로 한 거임)
    # cafe_stars_avg = ''
    # for cafe_stars in range(int(this_cafe.cafe_stars)): 
    #     cafe_stars_avg += '⭐'
    

    ctx={'this_cafe': this_cafe, 'each_reviews': each_reviews, 'review_photo': review_photo, 'cafe_stars_avg': cafe_stars_avg}

    return render(request, 'cafe/review_list.html', ctx)


def review_create(request, pk):
    if request.method == 'POST':
        #사진 제외한 review 요소들 저장
        form = ReviewForm(request.POST)
        if form.is_valid():
            myreview = form.save(commit=False)
            myreview.username = request.user
            myreview.cafe = CafeList.objects.get(pk=pk)
            myreview = form.save()

        #review_form.html의 name 속성이 imgs인 input 태그에서 받은 파일을 반복문으로 하나씩 가져온다.
        for img in request.FILES.getlist('imgs'):
            #photo 객체 하나 생성
            photo = ReviewPhoto()
            #외래키로 현재 생성한 review의 기본키 참조(지금 다루는 사진의 리뷰가 위에서 가져온 리뷰, 카페도 지정)
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
        cafe_list = CafeList.objects.order_by('-id')#나중에 ㄱㄴㄷ 순으로 바꿀?
        if search_keyword:
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
    cafes = CafeList.objects.all()
    cafe_list = serializers.serialize('json', cafes)
    ctx = {
        'data': cafe_list
    }
    return render(request, 'cafe/cafe_map.html', ctx)

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
    return redirect('home')