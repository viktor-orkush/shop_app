from builtins import dict

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404

from order.models import Order, OrderItem
from .models import Cart, CartItem
from shop.models import Product
import stripe
from django.conf import settings
from django.template.loader import get_template
from django.core.mail import EmailMessage

# def _cart_id(request):
#     cart = request.session_key
#     if not cart:
#         cart = request.session.create()
#     return cart
def _cart_id(request):
    if not request.session.session_key:
        cart = request.session.create()
    else:
        cart = request.session.session_key
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
    try:
        cart_item = CartItem.objects.get(product=product)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
        cart_item.save()
    except ObjectDoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        cart_item.save()
    return redirect('cart:cart_detail')


def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart:cart_detail')


def full_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = Product.objects.get(id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart:cart_detail')


def cart_detail(request, total=0, counter=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_total = int(total * 100)
    description = 'Perfect Cushion Shop - New Order'
    data_key = settings.STRIPE_PUBLISH_KEY
    if request.method == 'POST':
        # print(request.POST)
        try:
            token = request.POST['stripeToken']
            email = request.POST['stripeEmail']
            billingName = request.POST['stripeBillingName']
            billingAddress1 = request.POST['stripeBillingAddressLine1']
            billingCity = request.POST['stripeBillingAddressCity']
            billingPostcode = request.POST['stripeBillingAddressZip']
            billingCountry = request.POST['stripeBillingAddressCountryCode']
            shipingName = request.POST['stripeShippingName']
            shippingAddress1 = request.POST['stripeShippingAddressLine1']
            shippingCity = request.POST['stripeShippingAddressCity']
            shippingPostcode = request.POST['stripeShippingAddressZip']
            shippingCountry = request.POST['stripeShippingAddressCountryCode']
            customer = stripe.Customer.create(
                email=email,
                source=token
            )
            charge = stripe.Charge.create(
                amount=stripe_total,
                currency='usd',
                description=description,
                customer=customer.id
            )
            '''create the order ...'''
            try:
                order_details = Order.objects.create(
                    token=token,
                    total=total,
                    emailAddress=email,
                    billingName=billingName,
                    billingAddress1=billingAddress1,
                    billingCity=billingCity,
                    billingPostcode=billingPostcode,
                    billingCountry=billingCountry,
                    shippingName=shipingName,
                    shippingAddress1=shippingAddress1,
                    shippingCity=shippingCity,
                    shippingPostcode=shippingPostcode,
                    shippingCountry=shippingCountry
                )
                order_details.save()
                for order_item in cart_items:
                    oi = OrderItem.objects.create(
                        product=order_item.product.name,
                        quantity=order_item.quantity,
                        price=order_item.product.price,
                        order=order_details
                    )
                    oi.save()
                    '''Reduce stock when order is placed or saved'''
                    products = Product.objects.get(id=order_item.product.id)
                    products.stock = int(order_item.product.stock - order_item.quantity)
                    products.save()
                    order_item.delete()
                    '''The terminal print this message when the order is saved'''
                    print('The order has been created')
                # todo setting domain dns for send email to customer with sending information of order *** mailgun.com
                # try:
                #     '''Calling the sendEmail function'''
                #     sendEmail(order_details.id)
                #     print('The order email send to the customer.')
                # except IOError as e:
                #     return e
                return redirect('order:thanks', order_details.id)
            except ObjectDoesNotExist:
                print("Error - " + ObjectDoesNotExist)
        except stripe.error.CardError as e:
            print("Error" + e)
            return False, e
    return render(request, 'cart.html', dict(cart_items=cart_items, total=total, counter=counter, stripe_total=stripe_total, description=description, data_key=data_key))


def sendEmail(order_id):
    transaction = Order.objects.get(id=order_id)
    order_item = Order.objects.filter(order=transaction)
    try:
        subject = "Perfect Cushion Store - New Order #{}".format(transaction.id)
        to = ['{}'.format(transaction.emailAddress)]
        from_email = "order@perfectcushionstore.com"
        order_information ={
            "transaction": transaction,
            'order_items': order_item
        }
        message = get_template('email/email.html').render(order_information)
        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        msg.content_subtype = 'html'
        msg.send()
    except IOError as e:
        return e
