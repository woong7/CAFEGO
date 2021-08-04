from django.urls import path
from . import views

#app_name = "accounts"

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    #path('', views.home, name ="home"),
    path('', views.home1, name='home1'),
    path('blog/<int:blog_id>', views.detail, name="detail"),
    path('blog/new/', views.new, name="new"),
    path('blog/create/', views.create, name="create"),
]