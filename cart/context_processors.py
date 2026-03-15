from .models import CartItem

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()
    
    # Force Django to save the session and send the cookie to the browser
    request.session['cart_active'] = True 
    
    return request.session.session_key

def cart_item_count(request):
    # Filter items based on whether the user is logged in or a guest
    if request.user.is_authenticated:
        items = CartItem.objects.filter(user=request.user)
    else:
        items = CartItem.objects.filter(session_id=_cart_id(request), user=None)

    count = 0
    total = 0
    
    for item in items:
        count += item.quantity
        total += (item.product.price * item.quantity)

    return {
        'cart_count': count,
        'cart_items': items,
        'cart_total': total
    }