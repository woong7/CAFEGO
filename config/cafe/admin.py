from django.contrib import admin
from .models import CafeList, Review, Comment, Map, ReviewPhoto

# Register your models here

class CafeListAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'address', 'cafe_stars']
admin.site.register(CafeList, CafeListAdmin)


#리뷰사진 클래스를 inline으로 나타낸다.
class ReviewPhotoInline(admin.TabularInline):
    model = ReviewPhoto

#리뷰 클래스는 해당하는 사진 객체를 리스트로 관리한다.
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'cafe', 'username', 'review_stars']
    inlines = [ReviewPhotoInline,]

#리뷰모델을 등록하고, 리뷰 관리하는 리뷰클래스도 등록한다.
admin.site.register(Review, ReviewAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ['id',]
admin.site.register(Comment, CommentAdmin)

class MapAdmin(admin.ModelAdmin):
    list_display = ['id',]
admin.site.register(Map, MapAdmin)
    