from django.urls import path
from .views import *

app_name = "users"
urlpatterns = [
    path("signup-user/", register_customeruser, name="signup-user"),
    path("signup-lab/", register_lab, name="signup-lab"),
]
