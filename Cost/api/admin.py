from django.contrib import admin

from .models import Group


class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'description')
    search_fields = ('title', 'description')
    empty_value_display = '-пусто-'


admin.site.register(Group, GroupAdmin)
