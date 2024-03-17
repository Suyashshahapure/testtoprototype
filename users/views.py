from django.shortcuts import render
from .forms import CustomerUserForm, LabForm
from django.shortcuts import redirect
from django.contrib import messages


def register_customeruser(request):
    form = CustomerUserForm()
    if request.method == "POST":
        form = CustomerUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registered Successfully")

            return redirect("account_login")

    context = {"form": form}
    return render(request, "account/register_customer.html", context)


def register_lab(request):
    form = LabForm()
    if request.method == "POST":
        form = LabForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registered Successfully")

            return redirect("account_login")

    context = {"form": form}
    return render(request, "account/register_lab.html", context)
