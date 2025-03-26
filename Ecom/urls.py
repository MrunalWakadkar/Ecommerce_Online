from django.contrib import admin
from django.urls import path , include
from . import views 

urlpatterns = [
    path('', views.home , name="homepage"),
    path('index.html' , views.index ,name="indexpage"),
    path('signup.html',views.signup,name="sign_up_page"),
    path('signin.html',views.signin ,name="sign_in_page"),
    path('authsignin',views.authsignin ,name="auth_signin "),
    path('authsignup',views.authsignup ,name="auth_signup"),
    path('logout' ,views.logout_user, name="logout"),

    path('contact.html' ,views.contact , name="contactpage"),
    path('check-out/', views.checkout, name='checkout'),

    path('shop/', views.shop, name='shop'),

    path('category-product-list/<str:category>', views.category_product_list, name='category-product-list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    
    path('order-history/', views.order_history, name='order_history'),
    path('place_order' , views.place_order , name="placeorder"),

    path("profile/", views.view_profile, name="view_profile"),
    path("change-password/", views.change_password, name="change_password"),

    
]
