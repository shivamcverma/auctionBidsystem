from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from myapp.models import Category, AuctionItem, Bid
import json

def index(request):
    live_auctions = AuctionItem.objects.filter(is_active=True, end_time__gt=timezone.now()).order_by('end_time')[:3]
    categories = Category.objects.all()
    return render(request, "index.html", {
        'live_auctions': live_auctions,
        'categories': categories
    })

def signup_view(request):
    if request.method == "POST":
        data = request.POST
        username = data.get('username') or f"{data.get('f_name')}_{data.get('l_name')}".lower()
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('/login/?page=auth&tab=register')
        
        user = User.objects.create_user(
            username=username,
            email=data.get('email'),
            password=data.get('password'),
            first_name=data.get('f_name'),
            last_name=data.get('l_name')
        )
        messages.success(request, "Account created! Please sign in to continue.")
        return redirect('/login/?page=auth&tab=login')
    return redirect('login_page')

def login_view(request):
    if request.method == "POST":
        data = request.POST
        user = authenticate(username=data.get('username'), password=data.get('password'))
        
        if user:
            login(request, user)
            messages.success(request, "Welcome back!")
            
            next_page = request.POST.get('next')
            if next_page:
                return redirect(next_page)
            return redirect('index')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('/login/?page=auth&tab=login')
    
    return redirect('login_page')

def logout_view(request):
    logout(request)
    return redirect('index')

def login_page(request):
    # This renders the unified login/signup/dashboard template
    active_page = request.GET.get('page', 'auth')
    tab = request.GET.get('tab', 'login')
    
    context = {
        'active_page': active_page,
        'tab': tab,
        'categories': Category.objects.all(),
        'today': timezone.now(),
        'auctions': AuctionItem.objects.filter(is_active=True, end_time__gt=timezone.now()).order_by('end_time')[:5]
    }
    
    if request.user.is_authenticated:
        # Fetching dashboard data
        context['listings'] = AuctionItem.objects.filter(seller=request.user)
        context['my_bids'] = Bid.objects.filter(user=request.user).order_by('-timestamp')
        
    # Get a specific or featured item for the bidding page if requested
    if active_page == 'bid':
        item_id = request.GET.get('id')
        if item_id:
            context['auction'] = get_object_or_404(AuctionItem, id=item_id)
        else:
            context['auction'] = AuctionItem.objects.filter(is_active=True).first()
            
        if context['auction']:
            context['bid_history'] = Bid.objects.filter(item=context['auction']).order_by('-amount')[:10]

    return render(request, "login.html", context)

@login_required
def place_bid(request, item_id):
    if request.method == "POST":
        item = get_object_or_404(AuctionItem, id=item_id)
        amount = float(request.POST.get('amount', 0))
        
        # Validation
        if item.end_time <= timezone.now():
            return JsonResponse({'status': 'error', 'message': 'Auction has ended'})
        
        current_max = item.current_bid or item.starting_price
        if amount <= current_max:
            return JsonResponse({'status': 'error', 'message': f'Bid must be higher than ₹{current_max}'})
        
        # Create Bid
        Bid.objects.create(user=request.user, item=item, amount=amount)
        item.current_bid = amount
        item.save()
        
        return JsonResponse({'status': 'success', 'new_bid': amount})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def add_product(request):
    if request.method == "POST":
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        starting_price = request.POST.get('starting_price')
        end_time = request.POST.get('end_time')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        category = get_object_or_404(Category, id=category_id)
        
        AuctionItem.objects.create(
            title=title,
            category=category,
            starting_price=starting_price,
            end_time=end_time,
            description=description,
            image=image,
            seller=request.user
        )
        messages.success(request, "Product listed successfully!")
        return redirect('/login/?page=seller')
    return redirect('login_page')