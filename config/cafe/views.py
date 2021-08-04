from django.shortcuts import render, redirect
from .models import CafeList, Review
from .forms import ReviewForm

# Create your views here.
def review_list(request, pk):
    cafe = CafeList.objects.all(pk=pk) #카페 정보 불러옴
    reviews = Review.objects.filter(cafe_review=cafe.name) #해당 카페 리뷰만 불러옴
    
    cafe_stars = []
    for i  in range(cafe.stars):
        cafe_stars.append('⭐')
        i += 1

    ctx={'cafe': cafe, 'reviews': reviews, 'cafe_stars':cafe_stars}
    return render(request, template_name='review_list.html', context=ctx)


def review_create(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save()
            return redirect('cafe:review_list')
    else:
        form = ReviewForm()
        ctx = {'form': form}
        return render(request, template_name='review_form.html', context=ctx)