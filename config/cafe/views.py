from django.shortcuts import render, redirect
from django.core import serializers
from django.views.generic import ListView
from .models import CafeList, Review, ReviewPhoto, Comment
from .forms import ReviewForm
from django.contrib import messages
from django.db.models import Q
import json
import csv
import pandas as pd
from cafe.models import CafeList

# Create your views here.
def review_list(request, pk):
    this_cafe = CafeList.objects.get(pk=pk) #해당 카페 정보 불러옴
    each_reviews = Review.objects.filter(cafe=this_cafe) #해당 카페 리뷰만 불러옴
    review_photo = ReviewPhoto.objects.filter(review_cafe=this_cafe) 
    
    cafe_stars = ''
    for i  in range(int(this_cafe.cafe_stars)): 
        cafe_stars += '⭐'

    ctx={'this_cafe': this_cafe, 'each_reviews': each_reviews, 'cafe_stars':cafe_stars, 'review_photo': review_photo}

    return render(request, 'cafe/review_list.html', ctx)


def review_create(request):
    if request.method == 'POST':
        #사진 제외한 review 요소들 저장
        form = ReviewForm(request.POST)
        if form.is_valid():
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
        ctx = {'form': form}
        return render(request, 'cafe/review_form.html', ctx)

class CafeListView(ListView):
    model = CafeList
    #리스트 몇줄 표시
    paginate_by = 5
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

# 카페 지도
def cafe_map(request):
    with open('C:/Users/96jos/Desktop/piro/cafe_go/CAFEGO/config/cafe/csv/crawledminor.csv','r', encoding='utf-8') as f:
        dr = csv.DictReader(f)
        s = pd.DataFrame(dr)
    ss = []
    for i in range(len(s)):
        st = (s['stores'][i], s['X'][i], s['Y'][i],  s['road_address'][i])
        ss.append(st)


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
    return redirect('accounts:home')