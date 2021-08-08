from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static 

app_name = 'cafe'

urlpatterns = [
    #path('', view=views.cafe_info, name='cafe_info'), 카페 정보 확인 페이지로(지도위에 카페 정보)
    path('review_create/', view=views.review_create, name='review_create'), #리뷰 작성 페이지로
    path('review_list/<int:pk>/', view=views.review_list, name='review_list'), #해당 카페 리뷰 확인 페이지로
    path('cafe_search/', views.CafeListView.as_view(), name='cafe_list'), #카페 검색 페이지로
    #path('cafe_search/', view=views.cafe_search, name='cafe_search'), 
    #path('cafe_search/<str:q>', views.cafe_search)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)