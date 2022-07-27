from django.contrib import admin
from .models import Item, Categories, Bids, Comments, Watch_list, User
# Register your models here.


class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "active", "category")
    

class CategoriesAdmin(admin.ModelAdmin):
    list_display = ("id", "title")


class BidsAdmin(admin.ModelAdmin):
    list_display = ("id", "bid", "user", "item")


class CommentsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "comment", "item")


class Watch_listAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "item")


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email")





admin.site.register(Item, ItemAdmin)
admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Bids, BidsAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(Watch_list, Watch_listAdmin)
admin.site.register(User, UserAdmin)
