from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
admin.site.register(VisitedCafe)
admin.site.register(Drink)
admin.site.register(Badge)

#admin.site.register(User)