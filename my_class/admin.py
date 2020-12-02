from django.contrib import admin
from .models import *


class ProfileAdmin(admin.ModelAdmin):
	filter_horizontal = ('classes',)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Class)
admin.site.register(ProfileClass)
admin.site.register(Task)
admin.site.register(Files)
admin.site.register(Images)
