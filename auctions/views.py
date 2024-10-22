from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import *
import sweetify


def index(request):
    drop = Category.objects.all()
    auctions = Auctions.objects.filter(active = True)
    context = {
        'auctions': auctions,
        'drop': drop,
    }
    return render(request, "auctions/index.html", context)

def categories(request, category):
    drop = Category.objects.all()
    auction_category = Category.objects.get(name=category)
    auctions = Auctions.objects.filter(active = True, category = auction_category)
    context = {
        'auctions': auctions,
        'drop': drop,
    }
    return render(request, "auctions/index.html", context)
        
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            sweetify.toast(request, 'Logged Succesfully', icon="success", timer=3000)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

@login_required(login_url='/login')
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
        sweetify.toast(request, 'Registered Successfully', icon="success", timer=3000)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='/login')
def new_list(request):
    if request.POST:
        form = AuctionsForm(request.POST,request.FILES)
        if form.is_valid:
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            # form.save()
            sweetify.toast(request, 'Auction placed', icon="success", timer=3000)
            return redirect("index")
    else:
        return render(request,"auctions/new_list.html",{"form": AuctionsForm()})


@login_required(login_url='/login')
def listing_details(request, id):
    listing = Auctions.objects.get(pk=id)
    comments = Comment.objects.filter(auctions_id=id)
    user = request.user
    if listing.owner == request.user:
        is_owner = True
    else:
        is_owner = False
    BidForm = UpdatePriceForm()
    similar = Auctions.objects.filter(category=listing.category).exclude(id=listing.id)[:4]
    watchlist = Watchlist.objects.filter(user=request.user,auctions=listing)
    if len(watchlist) > 0:
        in_watch = True
    else:
        in_watch = False
    last_bid = Bid.objects.filter(auctions=listing)[:1]
    if listing.active == False and last_bid[0].user == request.user:
        msg = "You have won the auction"
    elif listing.active == False:
        msg = "Closed auction"
    else:
        msg = None
    context = {
        'listing': listing,
        'user': user,
        'comments': comments,
        'form': BidForm,
        'is_owner': is_owner,
        'similar': similar,
        'in_watch': in_watch,
        'msg': msg,
    }
    return render(request, "auctions/details.html", context)

@login_required(login_url='/login')
def commentView(request, id):
    auction = get_object_or_404(Auctions, id=id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.auctions = auction
            comment.user = request.user
            comment.save()
            return redirect(reverse('listing_details', args=[id]))
        else:
            return HttpResponse(f'{form.errors}')
    

@login_required(login_url='/login')
def update_price(request, auction_id):
    auction = get_object_or_404(Auctions, pk=auction_id)
    
    if request.method == 'POST':
        form = UpdatePriceForm(request.POST)
        
        if form.is_valid():
            new_price = form.cleaned_data['current_price']
            
            # Validar que el nuevo precio sea mayor que el precio actual
            if new_price > auction.current_price:
                # Actualizar el precio actual de la subasta
                auction.current_price = new_price
                auction.save()
                
                # Crear un objeto Bid para registrar la nueva oferta
                bid = Bid.objects.create(amount=new_price, auctions=auction, user=request.user)
                bid.save()
                return redirect('listing_details', id=auction_id)
            else:
                sweetify.toast(request, 'Price too low', icon="success", timer=3000)
        else:
            sweetify.toast(request, 'Something went wrong', icon="success", timer=3000)
    else:
        form = UpdatePriceForm()
        sweetify.toast(request, 'Bid placed', icon="success", timer=3000)
    return redirect('listing_details', id=auction_id)

@login_required(login_url='/login')
def watchlist_view(request):
    watchlist_items = Watchlist.objects.filter(user=request.user)
    auctions = [item.auctions for item in watchlist_items]
    context = {
        'items': auctions
    }
    return render(request, 'auctions/watchlist.html', context)

@login_required(login_url='/login')  
def watchlist_add(request,auction_id):
    auction = get_object_or_404(Auctions, id=auction_id)
    new_item = Watchlist(
        auctions = auction,
        user = request.user
    )
    new_item.save()
    sweetify.toast(request, 'Added to watchlist', icon="success", timer=3000)
    return redirect('watchlist')
    
@login_required(login_url='/login')
def closeAuction(request, id):
    listingData = Auctions.objects.get(pk=id)
    listingData.active = False
    listingData.save()
    sweetify.toast(request, 'Closed Auction', icon="success", timer=3000)
    return redirect('index')