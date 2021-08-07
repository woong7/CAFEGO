from django.shortcuts import render, redirect
from .models import CafeList, Review, ReviewPhoto, Comment
from .forms import ReviewForm
from django.db.models import Q
import json
from django.views.generic import ListView

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

# 일단 내가 했던거..
# def cafe_search(request):
#     all_cafe = CafeList.objects.all()
#     ctx = {
#         'all_cafe': all_cafe,
#         # "all_cafe_js": json.dumps([cafe.json() for cafe in all_cafe])
#     }

#     return render(request, 'cafe/cafe_list.html', ctx)

class CafeListView(ListView):
    model = CafeList
    #리스트 몇줄 표시
    paginate_by = 10
    template_name = 'cafe/cafe_list.html'
    context_object_name = 'cafe_list'

    def get_queryset(self):
        cafe_list = CafeList.objects.order_by('-id') #나중에 ㄱㄴㄷ 순으로 바꿀?
        return cafe_list

    #하단부에 숫자 범위를 커스텀
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

        return context


#doit!
# class cafe_search(CafeList):
#     paginate_by = None

#     def get_queryset(self):
#         #검색으로 받아온 값을 q에 저장
#         q = self.kwargs['q']
#         #카페 이름에 q를 포함하는 것을 필터링, 꼭 언더바 2개 쓰기, distinct는 중복 제거
#         cafe_list = CafeList.objects.filter(Q(name__contains=q)).distinct()
#         return cafe_list
        