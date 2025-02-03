from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *


class AccountInline(admin.StackedInline):
    model = UserAccount
    can_delete = False
    verbose_name_plural = 'Профили'


class UserAdmin(BaseUserAdmin):
    inlines = (AccountInline, )
    list_display = ('id', 'email', 'username', 'is_superuser', 'is_active')

    # def get_cart(self, instance):
    #     return instance.profile.cart
    # get_cart.short_description = 'Карзина'


admin.site.register(SiteProfile)
admin.site.register(Team)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)