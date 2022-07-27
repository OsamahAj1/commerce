from unicodedata import decimal
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import CharField


class User(AbstractUser):
    pass


class Categories(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.title}"

class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="item_user")
    title = models.CharField(max_length=64)
    des = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.URLField(max_length=200, blank=True)
    active = models.BooleanField(default=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name="item_categories")

    def __str__(self):
        return f"{self.title}"


class Bids(models.Model):
    bid = models.DecimalField(max_digits=6, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids_user")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="bids_item")


class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments_user")
    comment = models.TextField()
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="comments_item")


class Watch_list(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watch_user")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="watch_item")



