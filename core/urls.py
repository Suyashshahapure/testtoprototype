from django.urls import path
from .views import *

app_name = "core"
urlpatterns = [
    path("tests/<int:lab_user_id>/", user_tests, name="tests"),
    path("cart/", user_cart, name="user_cart"),
    path("my-orders/", user_orders, name="user_orders"),
    path("add-to-cart/<int:pk>/<int:lab_user_id>/", add_to_cart, name="add_to_cart"),
    path("remove-from-cart/<int:pk>/", remove_from_cart, name="remove_from_cart"),
    path("paymenthandler/", paymenthandler, name="paymenthandler"),
    path("redirect-user", redirect_user, name="redirect_user"),
    path("list-labs/", list_labs, name="list_labs"),
]
