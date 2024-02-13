# admin.py в приложении users

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'профиль'
    fk_name = 'user'
    fields = ('full_name', 'city', 'age', 'phone_number', 'referral_code', 'discount')  # Укажите здесь поля, которые вы хотите отобразить
    readonly_fields = ('referral_code',)  # Сделайте 'referral_code' только для чтения

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)

# Перерегистрируем модель User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
