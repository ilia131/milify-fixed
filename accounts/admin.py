from django.contrib import admin

# Register your models here.
from .models import UserListener ,SupportRequest

admin.site.register(UserListener)
@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):

    list_display = (
        "subject",
        "email",
        "user",
        "status",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "subject",
        "message",
        "email",
        "user__email",
        "user__username",
    )

    readonly_fields = (
        "id",
        "user",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 20