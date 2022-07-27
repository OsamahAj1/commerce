from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, Item, Categories, Bids, Comments, Watch_list
from django.template.defaulttags import register
from django.core.exceptions import ObjectDoesNotExist

@register.filter
def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def index(request):

    item = Item.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "item": item
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url='/login')
def create(request):
    if request.method == "POST":

        # errors checking

        if not request.POST["title"] or not request.POST["price"] or not request.POST["des"]:
            return render(request, "auctions/error.html", {
                "error": "Must Fill All Fields"
            })

        if not request.POST.get("in_category", False) and not request.POST.get("new_category", False):
            return render(request, "auctions/error.html", {
                "error": "Must Fill All Fields"
            })

        try:
            price = request.POST["price"]
            price = round(float(price), 2)

        except ValueError:
            return render(request, "auctions/error.html", {
                "error": "Price Must Be Postive Digit"
            })

        if request.POST.get("in_category", False) and request.POST.get("new_category", False):
            return render(request, "auctions/error.html", {
                "error": "Choose one category"
            })

        check = Categories.objects.all()
        for i in check:
            if i.title.upper() == request.POST.get("new_category", False).upper():
                return render(request, "auctions/error.html", {
                    "error": "Category already in auctions"
                })

        if request.POST.get("image", False):
            if len(request.POST["image"]) > 200:
                return render(request, "auctions/error.html", {
                    "error": "Image url is too long"
                })

        # get input from user
        if request.POST.get("new_category", False):
            new_category = request.POST["new_category"]
            category = Categories(title=new_category)
            category.save()
        
        else:
            category = request.POST["in_category"]
            category = Categories.objects.get(title=category)

        title = request.POST["title"]
        des = request.POST["des"]
        user = request.user


        # create new listing
        if request.POST.get("image", False):
            image = request.POST.get("image", False)
            item = Item(user=user, title=title, des=des, price=price, image=image, category=category)

        else:
            item = Item(user=user, title=title, des=des, price=price, category=category)
        
        item.save()

        # redirect to index
        return HttpResponseRedirect(reverse("list", args=(item.id,)))

    return render(request, "auctions/create.html", {
        "categories": Categories.objects.all()
    })


@login_required(login_url='/login')
def listing(request, item_id):
    try:
        watch = Watch_list.objects.get(user=request.user, item=item_id)
    except ObjectDoesNotExist:
        watch = None

    try:  
        item = Item.objects.get(pk=item_id)
    except ObjectDoesNotExist:
        return render(request, "auctions/error.html", {
            "error": "Page Not Found 404"
        })

    try:
        user = Bids.objects.get(item=item_id, bid=item.price)
    except ObjectDoesNotExist:
        user = None

    return render(request, "auctions/listing.html", {
        "item": item,
        "watch": watch,
        "user": user,
        "comments": Comments.objects.filter(item=item_id)
    })


@login_required(login_url='/login')
def watch_edit(request, item_id):
    if request.method == "POST":

        # get item
        item = Item.objects.get(pk=item_id)

        # if add
        if request.POST.get("add", False):
            watch = Watch_list(user=request.user, item=item)
            watch.save()
            return HttpResponseRedirect(reverse("list", args=(item.id,)))

        elif request.POST.get("watch", False):
            watch = Watch_list.objects.get(item=item, user=request.user)
            watch.delete()
            return HttpResponseRedirect(reverse("watch"))

        elif request.POST.get("index", False):
            check = Watch_list.objects.filter(user=request.user)
            if check:
                for i in check:
                    if i.item.title == item.title:
                        return render(request, "auctions/error.html",{
                            "error": "item is already in watchlist"
                        })
            watch = Watch_list(user=request.user, item=item)
            watch.save()
            return HttpResponseRedirect(reverse("index"))   

        else:
            watch = Watch_list.objects.get(item=item, user=request.user)
            watch.delete()
            return HttpResponseRedirect(reverse("list", args=(item.id,)))


@login_required(login_url='/login')
def watch(request):
    return render(request, "auctions/watch.html", {
        "watch": Watch_list.objects.filter(user=request.user)
    })


def isindb(number, item_id):
    for i in Bids.objects.filter(item=item_id):
        if float(i.bid) == number:
            return True
    return False


@login_required(login_url='/login')
def bid(request, item_id):
    if request.method == "POST":
        
        # get the item 
        item = Item.objects.get(pk=item_id)

        # errors checking
        if not request.POST["bid"]:
            return render(request, "auctions/error.html", {
                "error": "Must Provide Bid"
            })

        try:
            bid = round(float(request.POST["bid"]), 2)
        except ValueError:
            return render(request, "auctions/error.html", {
                "error": "Bid Must Be Postive Digit"
            })

        if bid < item.price or isindb(bid, item_id) is True:
            return render(request, "auctions/error.html", {
                "error": "Bid Must be bigger than current price."
            })

        # add bid to db
        b = Bids(bid=bid, user=request.user, item=item)
        b.save()

        # update current price
        item.price = bid
        item.save()

        return HttpResponseRedirect(reverse("list", args=(item.id,)))


@login_required(login_url='/login')
def close(request, item_id):
    if request.method == "POST":

        # get item
        item = Item.objects.get(pk=item_id)

        # close item
        item.active = False
        item.save()

        return HttpResponseRedirect(reverse("list", args=(item.id,)))


@login_required(login_url='/login')
def comment(request, item_id):
    if request.method == "POST":
        
        # error checking
        if not request.POST.get("comment"):
            return render(request, "auctions/register.html", {
                "message": "Must provide comment"
            })

        # get comment from user
        comment = request.POST["comment"]

        # get item
        item = Item.objects.get(pk=item_id)

        # create new comment
        com = Comments(comment=comment, user=request.user, item=item)
        com.save()

        return HttpResponseRedirect(reverse("list", args=(item.id,)))


@login_required(login_url='/login')
def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Categories.objects.all()
    })


@login_required(login_url='/login')
def category(request, category_id):
    try:
        category = Categories.objects.get(pk=category_id)
    except ObjectDoesNotExist:
        category = None
    return render(request, "auctions/index.html", {
        "item": Item.objects.filter(active=True, category=category_id),
        "category": category
    })
