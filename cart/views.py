from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from store.models import Product
from .models import CartItem

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()
    
    # Force Django to save the session and send the cookie to the browser
    request.session['cart_active'] = True 
    
    return request.session.session_key

# 1. The Add to Cart Logic (AJAX/Fetch friendly)
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(product=product, user=request.user)
    else:
        cart_item, created = CartItem.objects.get_or_create(product=product, session_id=_cart_id(request), user=None)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Recalculate count for the frontend badge
    if request.user.is_authenticated:
        cart_count = sum(item.quantity for item in CartItem.objects.filter(user=request.user))
    else:
        cart_count = sum(item.quantity for item in CartItem.objects.filter(session_id=_cart_id(request), user=None))

    return JsonResponse({'cart_count': cart_count})

# 2. The Main Cart Page View
def cart_view(request):
    if request.user.is_authenticated:
        items = CartItem.objects.filter(user=request.user).order_by('id')
    else:
        items = CartItem.objects.filter(session_id=_cart_id(request), user=None).order_by('id')
        
    total = sum(item.product.price * item.quantity for item in items)
    
    context = {
        "items": items,
        "total": total
    }
    return render(request, "cart/cart.html", context)

# 3. Increase Item Quantity
def increase_quantity(request, item_id):
    if request.user.is_authenticated:
        item = get_object_or_404(CartItem, id=item_id, user=request.user)
    else:
        item = get_object_or_404(CartItem, id=item_id, session_id=_cart_id(request), user=None)
    
    item.quantity += 1
    item.save()
    
    # Redirects back to exactly where they clicked the button (Cart Page or Drawer)
    return redirect(request.META.get("HTTP_REFERER", "/cart/"))

# 4. Decrease Item Quantity
def decrease_quantity(request, item_id):
    if request.user.is_authenticated:
        item = get_object_or_404(CartItem, id=item_id, user=request.user)
    else:
        item = get_object_or_404(CartItem, id=item_id, session_id=_cart_id(request), user=None)
        
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete() # If it drops below 1, remove it entirely
        
    return redirect(request.META.get("HTTP_REFERER", "/cart/"))

# 5. Remove Item Completely
def remove_from_cart(request, item_id):
    if request.user.is_authenticated:
        item = get_object_or_404(CartItem, id=item_id, user=request.user)
    else:
        item = get_object_or_404(CartItem, id=item_id, session_id=_cart_id(request), user=None)
        
    item.delete()
    return redirect(request.META.get("HTTP_REFERER", "/cart/"))