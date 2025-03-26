from django.shortcuts import render , redirect ,  get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login  , logout
from django.db import IntegrityError
from .models import Products, Category, Cart, Order , CartItem , OrderItem 
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# Create your views here.
def home(request):
    return render(request , 'index.html' ,{})

def index(request):
    return render(request ,'index.html' ,{})
def signin(request):
    return render(request , 'signin.html' ,{})

def signup(request):
    return render(request ,'signup.html' , {})

def authsignin(request):
    if request.method=='POST':
        username=request.POST["uname"]
        password = request.POST["psw"]

        user =authenticate(request , username=username , password=password)

        if user is not None:
            login(request , user)
            print("User logged in " ,user)
            return redirect(reverse('homepage'))
        else:
            print("Invalid creentials")
            return redirect('sign_up_page')


def authsignup(request):
    if request.method == "POST":
        username = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("psw", "").strip()

        if not username or not email or not password:
            return render(request, "signup.html", {"error": "All fields are required!"})

        # Check if email is already used
        if User.objects.filter(email=email).exists():
            return render(request, "signup.html", {"error": "Email already in use!"})

        # Split first and last name
        name_parts = username.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        try:
            # Create user
            user = User.objects.create_user(
                username=email,  # Use email as username
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Log the user in after successful registration
            login(request, user)

            print("User created successfully:", user)
            return redirect(reverse('sign_in_page'))  # Ensure 'homepage' exists in urls.py
        
        except IntegrityError:
            return render(request, "signup.html", {"error": "An error occurred while creating the user!"})

    return render(request, "signup.html")

def logout_user(request):
    logout(request)
    return redirect('/')

def category_product_list(request, category):
    products = Products.objects.filter(category__name=category)
    categories = Category.objects.all()
    return render(request, 'product-list.html', {'products': products, 'categories':categories})


def contact(request):
    return render(request , 'contact.html' ,{})

def checkout(request):
    return render(request , 'checkout.html' ,{})



def shop(request):
    categories = Category.objects.all()  # Fetch all categories
    category_filter = request.GET.get('category', '').strip()  # Get category from URL, strip spaces

    if category_filter:
        # Check if category exists before filtering
        if Category.objects.filter(name__iexact=category_filter).exists():
            products = Products.objects.filter(category__name__iexact=category_filter)  # Case-insensitive filtering
        else:
            products = Products.objects.none()  # No matching products
    else:
        products = Products.objects.all().order_by('-id')  # Show all products

    return render(request, "shop.html", {"products": products, "categories": categories, "selected_category": category_filter})



   

def product_detail(request, product_id):
    product = Products.objects.get(id = product_id)
    return render(request, 'product_detail.html', {"product":product})




   

@login_required
def checkout(request):
    """Handles order placement and payment selection"""
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect("shop")  

    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping_charge = 100 if subtotal > 0 else 0  
    grand_total = subtotal + shipping_charge

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        address = request.POST.get("address")
        city = request.POST.get("city")
        zip_code = request.POST.get("zip")
        phone = request.POST.get("phone")
        payment_method = request.POST.get("payment_method")

        # Ensure user selects a payment method
        if not payment_method:
            messages.error(request, "Please select a payment method.")
            return redirect("checkout")

        # Save order
        order = Order.objects.create(
            user=request.user,
            total_price=grand_total,
            payment_method=payment_method,
            status="Processing"
        )

        # Save order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Clear cart after placing order
        cart_items.delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect("order_history")  

    return render(request, "check-out.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping_charge": shipping_charge,
        "grand_total": grand_total,
    })


@login_required
def view_cart(request):
    """Displays all cart items for a logged-in user."""
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def add_to_cart(request, product_id):
    """Adds a product to the cart, or increases quantity if already in the cart."""
    product = get_object_or_404(Products, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        cart_item.quantity += 1  # Increase quantity if already exists
        cart_item.save()
    
    messages.success(request, f"{product.name} added to cart!")
    return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    """Removes an item from the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('view_cart')


@login_required
def clear_cart(request):
    """Clears all items from the cart."""
    CartItem.objects.filter(user=request.user).delete()
    messages.success(request, "Cart cleared successfully!")
    return redirect('view_cart')

def order_history(request):
    if not request.user.is_authenticated:
        return redirect("signin")  # Redirect to login if user is not authenticated

    orders = Order.objects.filter(user=request.user).order_by("-created_at").prefetch_related("items")

    return render(request, "order_history.html", {"orders": orders})


def place_order(request):
    if request.method == "POST":
        user = request.user
        if user.is_authenticated:
            # Get order details (modify as per your model)
            total_price = request.POST.get("total_price")
            payment_method = request.POST.get("payment_method")
            
            # Create and save the order
            order = Order.objects.create(
                user=user,
                total_price=total_price,
                payment_method=payment_method,
                status="Processing"
            )
            order.save()
            messages.success(request, "Order placed successfully!")
            return redirect("order_history")  # Change to your success page

        else:
            messages.error(request, "You need to log in first.")
            return redirect("login")

    return redirect("checkout")

@login_required
def view_profile(request):
    """Renders the user profile page."""
    return render(request, "view_profile.html")

@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")

        if not request.user.check_password(old_password):
            messages.error(request, "Old password is incorrect.")
            return redirect("change_password")

        if new_password1 != new_password2:
            messages.error(request, "New passwords do not match.")
            return redirect("change_password")

        request.user.set_password(new_password1)
        request.user.save()

        # Keep user logged in after password change
        update_session_auth_hash(request, request.user)

        messages.success(request, "Your password has been successfully changed.")
        return redirect("view_profile")

    return render(request, "change_password.html")
