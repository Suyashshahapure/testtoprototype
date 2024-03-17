from django.contrib import messages
from django.shortcuts import redirect


def allow_lab_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_lab_user:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "You are not allowed to view this page.")
                return redirect("account_login")
        else:
            messages.error(request, "You are not allowed to view this page.")
            return redirect("account_login")

    return wrapper_func


def allow_customer_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_lab_user:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "You are not allowed to view this page.")
                return redirect("account_login")
        else:
            messages.error(request, "You are not allowed to view this page.")
            return redirect("account_login")

    return wrapper_func
