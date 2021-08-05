from django.shortcuts import render, redirect
from .models import CafeList, Review, ReviewPhoto, Comment
from .forms import ReviewForm

# Create your views here.
def review_list(request, pk):
    cafe = CafeList.objects.get(pk=pk) #해당 카페 정보 불러옴
    reviews = Review.objects.filter(cafe=cafe.id) #해당 카페 리뷰만 불러옴
    review_photo = 
    #review_comments = Comment.objects.filter(review_comment=reviews.id)
    
    cafe_stars = ['⭐']
    # for i  in range(cafe.cafe_stars): #소숫점 때문에 별이 잘 안나올듯...
    #     cafe_stars.append('⭐')
    #     i += 1

    ctx={'cafe': cafe, 'reviews': reviews, 'cafe_stars':cafe_stars}
    return render(request, 'cafe/review_list.html', ctx)


def review_create(request):
    if request.method == 'POST':
        #사진 제외한 review 요소들 저장
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save()

        #review_form.html의 name 속성이 imgs인 input 태그에서 받은 파일을 반복문으로 하나씩 가져온다.
        for img in request.FILES.getlist('imgs'):
            #photo 객체 하나 생성
            photo = ReviewPhoto()
            #외래키로 현재 생성한 review의 기본키 참조(지금 다루는 사진의 리뷰가 위에서 가져온 리뷰)
            photo.review = review
            #imgs에서 가져온 이미지 파일 하나를 저장
            photo.image = img
            #db에 저장
            photo.save()
        
        #해당 리뷰를 쓴 카페 아이디 추출 (해당 카페의 리뷰를 전부 보려고 함)
        cafe = CafeList.objects.get(pk=review.cafe.id)
        
        return redirect('cafe:review_list', cafe.id)
    else:
        form = ReviewForm()
        ctx = {'form': form}
        return render(request, 'cafe/review_form.html', ctx)