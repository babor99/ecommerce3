from django.urls import path
from . views import *
# (HomeView, RegistrationView, LoginView, LogoutView, ProfileView, CategoryWiseView, ProductDetailView,
# AddToCartView,MyCartView,ManageCartView,EmptyCartView,CheckoutView,ContactView,AboutView)


app_name = 'ecomapp'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('forgot_password/', PasswordForgotView.as_view(), name='forgot_password'),
    path('password_reset/<email>/<token>/', PasswordResetView.as_view(), name='password_reset'),

    path('admin_login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin_home/', AdminHomeView.as_view(), name='admin_home'),
    path('admin_order_detail/<int:pk>/', AdminOrderDetailView.as_view(), name='admin_order_detail'),
    path('admin_all_orders/', AdminOrderListView.as_view(), name='admin_all_orders'),
    path('admin_order_status_change/<int:pk>/', AdminOrderStatusChangeView.as_view(), name='admin_order_status_change'),
    path('admin_product_list/', AdminProductListView.as_view(), name='admin_product_list'),
    path('admin_product_add/', AdminProductAddView.as_view(), name='admin_product_add'),

    path('search/', SearchView.as_view(), name='search'),

    path('category_wise/', CategoryWiseView.as_view(), name='category_wise'),
    path('product_detail/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),

    path('add_to_cart/<int:pro_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('my_cart/', MyCartView.as_view(), name='my_cart'),
    path('manage_cart/<int:cp_id>/', ManageCartView.as_view(), name='manage_cart'),
    path('empty_cart/', EmptyCartView.as_view(), name='empty_cart'),

    path('checkout/', CheckoutView.as_view(), name='checkout'),

    path('profile/', ProfileView.as_view(), name='profile'),

    path('order_detail/order-<int:pk>/', OrderDetailView.as_view(), name='order_detail'),

    path('contact/', ContactView.as_view(), name='contact'),
    path('about/', AboutView.as_view(), name='about'),
]