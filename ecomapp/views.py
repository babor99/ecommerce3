from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings

from .forms import *
from .models import *
from .utils import password_reset_token

# Create your views here.

class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/admin_login/")
        return super().dispatch(request, *args, **kwargs)


class HomeView(EcomMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        paginator = Paginator(products, 8)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        return context


class RegistrationView(CreateView):
    template_name = 'register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('ecomapp:home')


    def form_valid(self, form):
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)

        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('ecomapp:home')

    def form_valid(self, form):
        uname = form.cleaned_data['username']
        pword = form.cleaned_data['password']
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {'form':self.form_class, 'error': 'Invalid Credentials!'})

        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class LogoutView(View):
    def get(self, request):
        logout(self.request)
        return redirect('ecomapp:home')


class PasswordForgotView(FormView):
    template_name = 'forgot_password.html'
    form_class = ForgotPasswordForm
    success_url = "/forgot_password/?m=s"

    def form_valid(self, form):
        email = self.request.POST.get('email')
        customer = Customer.objects.get(user__email=email)
        user = customer.user
        url = self.request.META['HTTP_HOST'] # get current host ip/ domain
        text_content = 'Please click the link below to reset your password: '
        html_content = url + '/password_reset/' + email + '/' + password_reset_token.make_token(user) + '/'
        send_mail(
            'Password Reset | Manitoba Store',
            text_content + html_content,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return super().form_valid(form)


class PasswordResetView(FormView):
    template_name = 'password_reset.html'
    form_class = PasswordResetForm
    success_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        email = self.kwargs.get('email')
        user = User.objects.get(email=email)
        token = self.kwargs.get('token')
        if user is not None and password_reset_token.check_token(user, token):
            pass
        else:
            return redirect(reverse('ecomapp:forgot_password') + '?m=e')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        password = form.cleaned_data['new_password']
        email = self.kwargs.get('email')
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()

        return super().form_valid(form)


class AdminLoginView(FormView):
    template_name = 'admin/admin_login.html'
    form_class = LoginForm
    success_url = reverse_lazy('ecomapp:admin_home')

    def form_valid(self, form):
        uname = form.cleaned_data['username']
        pword = form.cleaned_data['password']
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {'form':self.form_class, 'error': 'Invalid Credentials!'})

        return super().form_valid(form)


class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = 'admin/admin_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_orders'] = Order.objects.filter(order_status='Order Received').order_by('-created_at')
        return context
    

class AdminOrderDetailView(AdminRequiredMixin, DetailView):
    template_name = 'admin/admin_order_detail.html'
    model = Order
    context_object_name = 'ord_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_status'] = ORDER_STATUS
        return context
        

class AdminOrderListView(AdminRequiredMixin, TemplateView):
    template_name = 'admin/admin_all_orders.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_orders'] = Order.objects.all().order_by('-id')
        return context


class AdminOrderStatusChangeView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs['pk']
        new_status = self.request.POST['status']
        order_obj = Order.objects.get(id=order_id)
        order_obj.order_status = new_status
        order_obj.save()
        return redirect(reverse_lazy('ecomapp:admin_order_detail', kwargs=({'pk':order_id})))


class AdminProductListView(AdminRequiredMixin, ListView):
    template_name = 'admin/admin_product_list.html'
    queryset = Product.objects.all().order_by('-id')
    context_object_name = 'all_products'


class AdminProductAddView(AdminRequiredMixin, FormView):
    template_name = 'admin/admin_product_add.html'
    form_class = AdminProductAddForm
    success_url = reverse_lazy('ecomapp:admin_product_list')

    def form_valid(self, form):
        p = form.save()
        extra_images = self.request.FILES.getlist('extra_images')
        for i in extra_images:
            ProductImage.objects.create(product=p, image=i)
        return super().form_valid(form)



class SearchView(TemplateView):
    template_name = 'search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data( **kwargs)
        kword = self.request.GET.get('keyword')
        searched_items = Product.objects.filter(title__icontains=kword)
        context['searched_items'] = searched_items
     
        return context


class CategoryWiseView(EcomMixin, TemplateView):
    template_name = 'category_wise.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('-id')
        return context


class ProductDetailView(EcomMixin, TemplateView):
    template_name = 'product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs['slug']
        product = Product.objects.get(slug=slug)
        product.view_count += 1
        product.save()
        extra_images = ProductImage.objects.filter(product=product)
        context['extra_images'] = extra_images
        context['product'] = product
        return context


class AddToCartView(EcomMixin, TemplateView):
    template_name = 'add_to_cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get product_id from requested url
        product_id = self.kwargs['pro_id']
        # get product
        product_obj = Product.objects.get(id=product_id)

        # check if cart exists
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)

            # if item exist in cart
            if this_product_in_cart.exists():
                cart_product = this_product_in_cart.first()
                cart_product.quantity += 1
                cart_product.subtotal += product_obj.selling_price
                cart_product.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
            # else add new item
            else:
                cart_product = CartProduct.objects.create(
                    cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1,
                    subtotal=product_obj.selling_price)
                cart_obj.total += product_obj.selling_price
                cart_obj.save()

        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cart_product = CartProduct.objects.create(
                cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1,
                subtotal=product_obj.selling_price)
            cart_obj.total += product_obj.selling_price
            cart_obj.save()
        return context


class MyCartView(EcomMixin, TemplateView):
    template_name = 'my_cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context

                                                                                                                                                             
class ManageCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs['cp_id']
        action = self.request.GET.get('action')
        print('cp_id: ', cp_id)
        print('action: ', action)
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart
        print('cp_obj', cp_obj)
        if action == 'increment':
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()

        elif action == 'decrement':
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()

            if cp_obj.quantity <= 0:
                cp_obj.delete()

        elif action == 'remove':
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()

        else:
            pass
        return redirect('ecomapp:my_cart')


class EmptyCartView(View):
    def get(self, request, **kwargs):
        cart_id = request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect('ecomapp:my_cart')


class CheckoutView(EcomMixin, CreateView):
    template_name = 'checkout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy('ecomapp:home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get('cart_id')
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.discount = 0
            form.instance.subtotal = cart_obj.total
            form.instance.total = cart_obj.total
            form.instance.order_status = 'Order Received'
            del self.request.session['cart_id']
        else:
            return redirect('ecomapp:home')
        return super().form_valid(form)


class ProfileView(TemplateView):
    template_name = 'profile.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        orders = Order.objects.filter(cart__customer=customer).order_by('-id')
        context['customer'] = customer
        context['orders'] = orders

        return context


class OrderDetailView(DetailView):
    template_name = 'detail_view.html'
    model = Order
    context_object_name = 'ord_obj'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs['pk']
            order = Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect('ecomapp:profile')
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)


class AboutView(EcomMixin, TemplateView):
    template_name = 'about.html'


class ContactView(EcomMixin, TemplateView):
    template_name = 'contact.html'

    