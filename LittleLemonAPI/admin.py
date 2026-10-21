from django.contrib import admin
from .models import (
    Category,
    MenuItem,
    Cart,
    Order,
    OrderItem
)
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authtoken.models import Token, TokenProxy


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "slug"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ("title",)}

class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "get_groups",
        "is_staff",
    )

    def get_groups(self, obj):
        return ", ".join(
            group.name for group in obj.groups.all()
        )

    get_groups.short_description = "Groups"


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class CustomTokenAdmin(TokenAdmin):
    list_display = ("key", "user", "get_groups", "created")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user").prefetch_related("user__groups")

    @admin.display(description="Groups")
    def get_groups(self, obj):
        return ", ".join(group.name for group in obj.user.groups.all())


admin.site.unregister(TokenProxy)
admin.site.register(Token, CustomTokenAdmin)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "price",
        "featured",
        "category",
    )

    list_filter = (
        "featured",
        "category",
    )

    search_fields = (
        "title",
    )

    ordering = (
        "title",
    )

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "menuitem",
        "quantity",
        "unit_price",
        "price",
    )

    list_filter = (
        "user",
        "menuitem",
    )

    search_fields = (
        "user__username",
        "menuitem__title",
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "delivery_crew",
        "status",
        "total",
        "date",
    )

    list_filter = (
        "status",
        "date",
    )

    search_fields = (
        "user__username",
        "delivery_crew__username",
    )

    ordering = ("-date",)
    
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "menuitem",
        "quantity",
        "unit_price",
        "price",
    )

    list_filter = (
        "order",
        "menuitem",
    )

    search_fields = (
        "menuitem__title",
    )

    ordering = ("id",)
