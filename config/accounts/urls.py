from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static 
import os

#app_name = "accounts"

urlpatterns = [
    path('', views.main, name='main'),
    path('home/', views.home, name='home'),
    path('signup/', views.UserRegistrationView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'), #views.login
    path('logout/', views.logout, name='logout'),
    path('mypage/<int:pk>', views.mypage, name='mypage'),
    #path('info_edit/<int:pk>/', views.InfoUpdateView.as_view(), name='info_edit'),
    path('info_edit/<int:pk>/', views.infoupdate, name='info_edit'),
    path('addfriend/<int:pk>', views.addfriend, name='addfriend'),
    path('deletefriend/<int:pk>', views.deletefriend, name='deletefriend'),
    path('friend_search', views.FriendSearchListView.as_view(), name='friend_search'),
    path('friend_register/', views.friend_register, name="friend_register"),
    path('create_admin/', views.create_admin, name="create_admin"),
    path('<pk>/verify/<token>/', views.UserVerificationView.as_view(), name="verify"),

    path('badge/list/<int:pk>', views.badge_list, name='badge_list'),
    path('badge/taken/', views.badge_taken, name='badge_taken'),
    path('badge/untaken/', views.badge_untaken, name='badge_untaken'),
    path('myreview_list/', views.MyCafeReviewListView.as_view(), name='myreview_list'),
    path('review_update/<int:pk>/', views.review_update, name='review_update'),
    path('rank/list/', views.rank_list, name='rank_list'),
    path('rank/detail/', views.rank_detail, name='rank_detail'),
    path('cafemap/', views.user_cafe_map, name='user_cafe_map'),
    path('this_cafe_map/<int:pk>/', views.this_cafe_map, name='this_cafe_map'),
    #path('detail/', views.user_detail, name='user_detail'),

    path('enroll_home/', views.enroll_home, name="enroll_home"),
    path('visit_register/', views.visit_register, name="visit_register"),
    path('visited_register/', views.visited_register, name="visited_register"),
    path('enroll_new_cafe/', views.EnrollNewCafeListView.as_view(), name="enroll_new_cafe"),
    path('enroll_visited_cafe/', views.EnrollVisitedCafeListView.as_view(), name="enroll_visited_cafe"),
    
    path('notification/<int:notification_pk>/comment/<int:review_pk>', views.CommentNotification.as_view(), name='comment-notification'),
    path('notification/<int:notification_pk>/profile/<int:user_pk>', views.FollowNotification.as_view(), name='follow-notification'),
    path('notification/delete/<int:notification_pk>', views.RemoveNotification.as_view(), name='notification-delete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)