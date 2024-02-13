# admin.py в приложении support

from django.contrib import admin
from .models import Ticket, Response


class ResponseInline(admin.TabularInline):
    model = Response
    extra = 1
    fields = ('user', 'content', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'content', 'user__username')
    inlines = [ResponseInline]
    fields = ('title', 'user', 'content', 'status', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'content', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('content', 'ticket__title', 'user__username')
    fields = ('ticket', 'user', 'content', 'created_at')
    readonly_fields = ('created_at',)
