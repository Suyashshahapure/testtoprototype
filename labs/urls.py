from django.urls import path
from .views import *

app_name = "labs"
urlpatterns = [
    path("my-tests/", my_tests, name="my_tests"),
    path("lab-orders/", lab_orders, name="lab_orders"),
    path("complete-order/<int:pk>/", complete_order, name="complete_order"),
    path("create-user/", create_test, name="create_test"),
    path("delete-test/<int:pk>/", delete_test, name="delete_test"),
    path("update-test/<int:pk>/", update_test, name="update_test"),
]
