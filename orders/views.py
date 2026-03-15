from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from cart.models import CartItem
from .models import Order, OrderItem

# 1. Helper function to manage guest sessions and fix the "Ghost Session" bug
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()
    
    # CRITICAL: Forces Django to save the session and send the cookie to the browser
    request.session['cart_active'] = True 
    return request.session.session_key

# 2. Secure Checkout View
def checkout(request):
    # Fetch ONLY the items for this specific user/session
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        current_user = request.user
    else:
        cart_items = CartItem.objects.filter(session_id=_cart_id(request), user=None)
        current_user = None

    # Block checkout if the cart is empty
    if not cart_items.exists():
        return redirect('/')

    # Calculate total for the frontend UI
    total = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        address = request.POST.get("address")

        # Create the Order (safely handles guest checkouts by passing None to user)
        order = Order.objects.create(
            user=current_user,
            name=name,
            email=email,
            address=address
        )

        # Move items from Cart to OrderItems
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Clear the user's cart now that the order is placed
        cart_items.delete()

        return redirect(f"/order-success/{order.id}/")

    # Pass the total so your new premium UI can display it
    context = {
        "cart_items": cart_items,
        "cart_total": total
    }
    return render(request, "orders/checkout.html", context)

# 3. Secure Order Success View
def order_success(request, order_id):
    # Use get_object_or_404 to prevent server crashes if a user types a fake ID in the URL
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/order_success.html", {"order": order})

# 4. Secure Order History View
@login_required(login_url='/accounts/login/')
def my_orders(request):
    # Only logged-in users can access this page
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders/my_orders.html", {"orders": orders})
