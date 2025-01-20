from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *


class ProfileInline(admin.StackedInline):
    model = UserAccount
    can_delete = False
    verbose_name_plural = 'Профили'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )
    list_display = ()

    # def get_cart(self, instance):
    #     return instance.profile.cart
    # get_cart.short_description = 'Карзина'


admin.site.register(SiteProfile)
admin.site.register(Team)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)