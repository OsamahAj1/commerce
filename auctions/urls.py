from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("list/<int:item_id>", views.listing, name="list"),
    path("watch/<int:item_id>", views.watch_edit, name="watch_edit"),
    path("watch", views.watch, name="watch"),
    path("bid/<int:item_id>", views.bid, name="bid"),
    path("close/<int:item_id>", views.close, name="close"),
    path("comment/<int:item_id>", views.comment, name="comment"),
    path("categories", views.categories, name="categories"),
    path("home/<int:category_id>", views.category, name="category")
]
