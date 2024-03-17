from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .utils import allow_lab_user
from .models import Test, Order
from .forms import TestForm, CompleteOrderForm
from django.utils import timezone
from django.contrib import messages

# create views for creating, updating, deleting and listing tests


@login_required
@allow_lab_user
def my_tests(request):

    my_tests = Test.objects.filter(user=request.user)

    return render(request, "labs/my_tests.html", {"my_tests": my_tests})


# create test
@login_required
@allow_lab_user
def create_test(request):
    form = TestForm()
    if request.method == "POST":
        form = TestForm(request.POST, request.FILES)
        if form.is_valid():
            test_obj = form.save(commit=False)
            test_obj.user = request.user
            test_obj.save()
            messages.success(request, "Created Successfully")
            return redirect("labs:my_tests")
    return render(request, "labs/create_test.html", {"form": form})


# update test
@login_required
@allow_lab_user
def update_test(request, pk):
    test = Test.objects.get(id=pk)
    form = TestForm(instance=test)
    if request.method == "POST":
        form = TestForm(request.POST, request.FILES, instance=test)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated Successfully")

            return redirect("labs:my_tests")
    return render(request, "labs/update_test.html", {"form": form, "test": test})


# delete test
@login_required
@allow_lab_user
def delete_test(request, pk):
    test = Test.objects.get(id=pk)
    test.delete()
    messages.error(request, "Deleted Successfully")

    return redirect("labs:my_tests")


def complete_order(request, pk):
    order = Order.objects.get(id=pk)
    form = CompleteOrderForm(instance=order)
    if request.method == "POST":
        form = CompleteOrderForm(request.POST, request.FILES, instance=order)
        if form.is_valid():
            form.save()
            order.completed = timezone.now()
            order.save()

            messages.success(request, "Order Completed Successfully")
            return redirect("labs:lab_orders")
    return render(request, "labs/complete_order.html", {"form": form, "order": order})


# test orders
def lab_orders(request):
    orders = Order.objects.filter(
        lab_user=request.user, placed__isnull=False, completed__isnull=True
    ).order_by("-placed")
    completed_orders = Order.objects.filter(
        lab_user=request.user, completed__isnull=False
    ).order_by("-completed")

    return render(
        request,
        "labs/orders.html",
        {"orders": orders, "completed_orders": completed_orders},
    )
