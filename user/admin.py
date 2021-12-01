from django.contrib import admin
from .models import *


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('uid' , 'username' , 'password' )
    list_filter = ('created_at','updated_at')

# class Userset(admin.ModelAdmin):
#     list_display = ['uid','account','password','email']
#     list_filter = ('created_at','updated_at')

# class deflat(admin.ModelAdmin):
#     list_display = ['uid','account','password','email']
#     list_filter = ('created_at','updated_at')

admin.site.register(UserProfile,UserProfileAdmin)
admin.site.register(UserSet)
admin.site.register(deflat)
admin.site.register(medicalinformation)
admin.site.register(druginformation)
admin.site.register(HbA1c)
admin.site.register(Notification)
admin.site.register(Share)
# Register your models here.
