from django.contrib import admin
from .models import CafeList, Review, Comment, Map

# Register your models here
admin.site.register(CafeList)
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(Map)