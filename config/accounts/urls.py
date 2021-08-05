from django.urls import path
from . import views

#app_name = "accounts"

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.LoginView.as_view(), name='login'), #views.login
    path('logout/', views.logout, name='logout'),
    #path('', views.home, name ="home"),
    path('', views.main, name='main'),
    path('home/', views.home, name='home'),

]