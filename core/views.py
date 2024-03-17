from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from labs.utils import allow_customer_user
from labs.models import Test, Order
from users.models import User
from django.contrib import messages
from django.utils import timezone

import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.db.models import Q


# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET)
)


@allow_customer_user
@login_required
def user_tests(request, lab_user_id):
    lab = User.objects.get(id=lab_user_id)
    all_tests = Test.objects.filter(user_id=lab_user_id, available=True)
    if request.method == "GET":
        search_query = request.GET.get("search", "")
        search_query = search_query.strip()
        if search_query:
            all_tests = all_tests.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        return render(
            request,
            "users/tests.html",
            {"all_tests": all_tests, "lab": lab, "search_query": search_query},
        )


def list_labs(request):
    if request.method == "GET":
        search_query = request.GET.get("search", "")
        search_query = search_query.strip()
        address_query = request.GET.get("address", "").strip()
        print(address_query)
        if search_query or address_query:
            if search_query and address_query:
                list_of_labs = User.objects.filter(
                    Q(first_name__icontains=search_query)
                    | Q(last_name__icontains=search_query),
                    Q(address__full_address__icontains=address_query),
                    is_lab_user=True,
                )
            elif search_query:
                list_of_labs = User.objects.filter(
                    Q(first_name__icontains=search_query)
                    | Q(last_name__icontains=search_query),
                    is_lab_user=True,
                )
            else:

                list_of_labs = User.objects.filter(
                    # Q(first_name__icontains=search_query)
                    # | Q(last_name__icontains=search_query)
                    Q(address__full_address__icontains=address_query),
                    is_lab_user=True,
                )

        else:
            list_of_labs = User.objects.filter(is_lab_user=True)

        return render(
            request,
            "users/list_labs.html",
            {
                "list_of_labs": list_of_labs,
                "search_query": search_query,
                "address_query": address_query,
            },
        )


@login_required
def redirect_user(request):
    if request.user.is_lab_user:
        return redirect("labs:my_tests")
    else:
        return redirect("core:list_labs")


@login_required
@allow_customer_user
def user_cart(request):
    currency = "INR"
    order = Order.objects.filter(user=request.user, placed=None)
    if order.exists():
        order = order[0]
        if order.items.count() == 0:
            messages.error(request, "Please add tests to cart first")
            return redirect("core:list_labs")
    else:
        messages.error(request, "Please add tests to cart first")
        return redirect("core:list_labs")
    amount = order.get_total_price() * 100

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(
        dict(
            amount=amount,
            currency=currency,
            payment_capture="0",
            notes={
                "order_id": order.id,
                "type": "product",
            },
        ),
    )

    # order id of newly created order.
    razorpay_order_id = razorpay_order["id"]
    callback_url = "/paymenthandler/"
    print(razorpay_order)

    # we need to pass these details to frontend.
    context = {}
    context["razorpay_order_id"] = razorpay_order_id
    context["razorpay_merchant_key"] = settings.RAZOR_KEY_ID
    context["razorpay_amount"] = amount
    context["currency"] = currency
    context["callback_url"] = callback_url

    context["order"] = order

    return render(request, "users/cart.html", context)


# add test to cart(order)
@login_required
@allow_customer_user
def add_to_cart(request, pk, lab_user_id):
    test = Test.objects.get(id=pk)
    order, created = Order.objects.get_or_create(user=request.user, placed=None)

    # check if test is only from the same lab
    # get first test from the order
    if order.items.all().exists():
        first_test = order.items.all()[0]
        if first_test.user_id != lab_user_id:
            messages.error(request, "Please add tests from the same lab")
            return redirect("core:list_labs")

    if order.items.filter(id=test.id).exists():
        messages.error(request, "Test already in cart")
    else:
        # order.items.add(test)

        order.items.add(test)
        order.lab_user_id = lab_user_id
        order.save()
        messages.success(request, "Test added to cart successfully")

    return redirect("core:user_cart")


# remove test from cart(order)
@login_required
@allow_customer_user
def remove_from_cart(request, pk):
    test = Test.objects.get(id=pk)
    order = Order.objects.get(user=request.user, placed=None)

    order.items.remove(test)
    messages.error(request, "Test removed from cart successfully")

    return redirect("core:user_cart")


# user orders
@login_required
@allow_customer_user
def user_orders(request):
    orders = Order.objects.filter(
        user=request.user, placed__isnull=False, completed__isnull=True
    ).order_by("-placed")
    completed_orders = Order.objects.filter(
        user=request.user, completed__isnull=False
    ).order_by("-completed")

    return render(
        request,
        "users/orders.html",
        {"orders": orders, "completed_orders": completed_orders},
    )


@csrf_exempt
def paymenthandler(request):
    # only accept POST request.
    if request.method == "POST":
        print("post data ", request.POST)
        # get the required parameters from post request.
        try:
            payment_id = request.POST.get("razorpay_payment_id", "")
            razorpay_order_id = request.POST.get("razorpay_order_id", "")
            signature = request.POST.get("razorpay_signature", "")
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
            print("params_dict ", params_dict)

            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            print("result ", result)
            if result is not None:
                data = razorpay_client.order.fetch(razorpay_order_id)
                print("data ", data)

                order_id = data.get("notes").get("order_id")
                print("order_id ", order_id)
                print("NOTES", data.get("notes"))

                order = Order.objects.get(id=int(order_id))
                order.place_order()
                order.paid = timezone.now()
                order.save()

                try:
                    # capture the payemt
                    print(payment_id)
                    o = razorpay_client.payment.capture(
                        payment_id, order.get_total_price() * 100
                    )
                    print("jdnfv", o)

                    # render success page on successful caputre of payment\
                    messages.success(request, "Payment Successful !")
                    return redirect("core:user_orders")
                except Exception as e:
                    print("Exception ", e)
                    # if there is an error while capturing payment.
                    return redirect("core:user_cart")

            else:
                # if signature verification fails.
                return redirect("core:user_cart")
        except:
            messages.error(request, "Payment Failed")
            return redirect("core:user_cart")
            # if we don't find the required parameters in POST data
    else:
        # if other than POST request is made.
        messages.error(request, "Payment Failed")
        return redirect("core:user_cart")
