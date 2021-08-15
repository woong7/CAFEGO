from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
class VisitedCafeAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at',)
    admin.site.register(VisitedCafe)

admin.site.register(Drink)
admin.site.register(Badge)
admin.site.register(Notification)
#admin.site.register(User)