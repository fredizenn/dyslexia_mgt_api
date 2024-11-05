from django.contrib import admin

from user.models import Exercise, Profile, TextContent


admin.site.register(Profile)
admin.site.register(Exercise)
admin.site.register(TextContent)
# Register your models here.
