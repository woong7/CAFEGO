from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static 
import os

#app_name = "accounts"

urlpatterns = [
    path('', views.main, name='main'),
    path('home/', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.LoginView.as_view(), name='login'), #views.login
    path('logout/', views.logout, name='logout'),
    path('mypage/<int:pk>', views.mypage, name='mypage'),
    path('addfriend/<int:pk>', views.addfriend, name='addfriend'),
    path('deletefriend/<int:pk>', views.deletefriend, name='deletefriend'),
    path('friend_search', views.FriendSearchListView.as_view(), name='friend_search'),
    path('friend_register/', views.friend_register, name="friend_register"),

    path('badge/list/', views.badge_list, name='badge_list'),
    path('badge/taken/', views.badge_taken, name='badge_taken'),
    path('badge/untaken/', views.badge_untaken, name='badge_untaken'),
    path('cafemap/', views.user_cafe_map, name='user_cafe_map'),
    #path('detail/', views.user_detail, name='user_detail'),
    path('rank/detail/', views.rank_detail, name='rank_detail'),
    path('rank/list/', views.rank_list, name='rank_list'),

    path('enroll_home/', views.enroll_home, name="enroll_home"),
    path('visit_register/', views.visit_register, name="visit_register"),
    path('visited_register/', views.visited_register, name="visited_register"),
    path('enroll_new_cafe/', views.EnrollNewCafeListView.as_view(), name="enroll_new_cafe"),
    path('enroll_visited_cafe/', views.EnrollVisitedCafeListView.as_view(), name="enroll_visited_cafe"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)