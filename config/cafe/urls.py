from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static 

app_name = 'cafe'

urlpatterns = [
    #path('', view=views.cafe_info, name='cafe_info'), 카페 정보 확인 페이지로(지도위에 카페 정보)
    path('review_create/', view=views.review_create, name='review_create'), #리뷰 작성 페이지로
    path('review_list/', view=views.review_list, name='review_list'), #해당 카페 리뷰 확인 페이지로
    # path('review_map/', view=views.review_map, name='review_map'), #지도 위헤 리뷰 페이지로
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)