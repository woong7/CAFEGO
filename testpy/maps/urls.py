from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static

app_name = 'maps'

urlpatterns = [
    path('', views.maps_test, name='maps_test'),
] 
