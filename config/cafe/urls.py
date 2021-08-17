from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static 

app_name = 'cafe'

urlpatterns = [
    #path('', view=views.cafe_info, name='cafe_info'), 카페 정보 확인 페이지로(지도위에 카페 정보)
    path('review_create/<int:pk>/', view=views.review_create, name='review_create'), #리뷰 작성 페이지로
    path('review_list/<int:pk>/', view=views.review_list, name='review_list'), #해당 카페 리뷰 확인 페이지로
    path('cafe_search/', views.CafeListView.as_view(), name='cafe_list'), #카페 검색 페이지로
    path('cafe_map/', views.cafe_map, name='cafe_map'), # 카카오맵 카페 지도
    path('init_data/', views.init_data, name='init_data'),
    path('sort_latest/<int:pk>/', views.sort_latest, name='sort_latest'),
    path('sort_visit/<int:pk>/', views.sort_visit, name='sort_visit'),
    path('sort_total_visit/<int:pk>/', views.sort_total_visit, name='sort_total_visit'),
    path('sort_review/<int:pk>/', views.sort_review, name='sort_review'),
    path('comment_write/', views.comment_write, name='comment_write'),
    path('comment_delete/', views.comment_delete, name='comment_delete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)