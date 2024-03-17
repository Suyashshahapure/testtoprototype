from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinLengthValidator


class User(AbstractUser):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    username = models.CharField(
        "Phone Number",
        max_length=10,
        unique=True,
        validators=[
            MinLengthValidator(10),
            RegexValidator(regex=r"^\d*$", message="Only digits are allowed."),
        ],
    )
    is_lab_user = models.BooleanField(default=False, null=True, blank=True)
    address = models.JSONField(default=dict)
    pincode = models.CharField("Unique pin code", max_length=6)

    def get_user_profile_link(self):
        return f"https://ui-avatars.com/api/?name={self.first_name}+{self.last_name}&size=128&bold=true&background=random"
