from django.contrib import admin

from user.models import Exercise, Profile


admin.site.register(Profile)
admin.site.register(Exercise)
# Register your models here.
