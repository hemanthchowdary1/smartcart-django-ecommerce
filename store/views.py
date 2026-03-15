from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Review
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Wishlist
from django.db.models import Count
from django.db import IntegrityError
from django.contrib import messages

def product_list(request):

    trending_products = Product.objects.annotate(
        review_total=Count("reviews")
    ).order_by("-review_total")[:6]

    products = Product.objects.exclude(
        id__in=trending_products.values_list("id", flat=True)
    )

    categories = Category.objects.all()

    category_id = request.GET.get('category')
    search = request.GET.get('search')
    sort = request.GET.get('sort')

    if category_id:
        products = products.filter(category_id=category_id)

    if search:
        products = products.filter(name__icontains=search)

    if sort == "price_low":
        products = products.order_by("price")

    elif sort == "price_high":
        products = products.order_by("-price")

    elif sort == "newest":
        products = products.order_by("-created_at")

    recommended_products = []

    if request.user.is_authenticated:
        wishlist_products = Wishlist.objects.filter(
            user=request.user
        ).values_list("product__category", flat=True)

        recommended_products = Product.objects.filter(
            category__in=wishlist_products
        ).exclude(
            id__in=Wishlist.objects.filter(
                user=request.user
            ).values_list("product", flat=True)
        )[:6]

    context = {
        "products": products,
        "categories": categories,
        "trending_products": trending_products,
        "recommended_products": recommended_products,
    }

    return render(request, "store/product_list.html", context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        name = request.POST.get("name")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        Review.objects.create(
            product=product,
            name=name,
            rating=rating,
            comment=comment
        )
        # FIX: Redirect to the same page to prevent form resubmission on refresh
        return redirect('product_detail', product_id=product.id) 

    related_products = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.id
    ).annotate(
        review_count=Count("reviews")
    ).order_by("-review_count")[:4]

    reviews = Review.objects.filter(product=product)

    context = {
        "product": product,
        "related_products": related_products,
        "reviews": reviews
    }
    return render(request, "store/product_detail.html", context)

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # FIX: Check if username already exists to prevent a 500 Server Error
        if User.objects.filter(username=username).exists():
            return render(request, "registration/signup.html", {"error": "Username is already taken."})

        user = User.objects.create_user(
            username=username,
            password=password
        )
        login(request, user)
        return redirect("/")

    return render(request, "registration/signup.html")

def user_logout(request):
    logout(request)
    return redirect("/accounts/login/")

@login_required
def add_to_wishlist(request, product_id):
    # FIX: Prevents crash if product doesn't exist
    product = get_object_or_404(Product, id=product_id) 

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).order_by("-id")

    return render(request, "store/wishlist.html", {
        "items": items
    })

@login_required
def remove_from_wishlist(request, item_id):
    item = Wishlist.objects.get(id=item_id, user=request.user)
    item.delete()

    return redirect("/wishlist/")
