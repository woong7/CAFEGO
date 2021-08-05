from django.shortcuts import render, redirect
from .models import CafeList, Review, Comment
from .forms import ReviewForm

# Create your views here.
def review_list(request, pk):
    cafe = CafeList.objects.all(pk=pk) #해당 카페 정보 불러옴
    reviews = Review.objects.filter(cafe_review=cafe.id) #해당 카페 리뷰만 불러옴
    review_comments = Comment.objects.filter(review_comment=reviews.id)
    
    cafe_stars = []
    for i  in range(cafe.cafe_stars): #소숫점 때문에 별이 잘 안나올듯...
        cafe_stars.append('⭐')
        i += 1

    ctx={'cafe': cafe, 'reviews': reviews, 'cafe_stars':cafe_stars, 'review_comments': review_comments}
    return render(request, 'cafe/review_list.html', ctx)


def review_create(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cafe:review_list')
    else:
        form = ReviewForm()
        ctx = {'form': form}
        return render(request, 'cafe/review_form.html', ctx)