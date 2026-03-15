from django.urls import path
from . import views
from .views import product_list, product_detail, signup, user_logout, add_to_wishlist, wishlist_view, remove_from_wishlist

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path("signup/", signup, name="signup"),
    path("logout/", user_logout, name="logout"),
    path("wishlist/", wishlist_view, name="wishlist"),
    path("wishlist/add/<int:product_id>/", add_to_wishlist, name="add_to_wishlist"),
    path("wishlist/remove/<int:item_id>/", remove_from_wishlist, name="remove_from_wishlist"),
]
