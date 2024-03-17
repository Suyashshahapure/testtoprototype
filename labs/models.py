from django.db import models

from users.models import User
from django.utils import timezone


class Test(models.Model):
    """
    Represents a test in the laboratory.

    Attributes:
        name (str): The name of the test.
        description (str): The description of the test.
        user (User): The user associated with the test.
        price (Decimal): The price of the test.
        image (ImageField): The image associated with the test.
        created_at (DateTimeField): The date and time when the test was created.
        updated_at (DateTimeField): The date and time when the test was last updated.
    """

    name = models.CharField(max_length=100)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def number_of_orders(self):
        return Order.objects.filter(items=self, paid__isnull=False).count()

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(
        User,
        related_name="orders",
        on_delete=models.SET_NULL,
        null=True,
    )
    items = models.ManyToManyField(Test)
    placed = models.DateTimeField(null=True, blank=True)
    paid = models.DateTimeField(null=True, blank=True)
    completed = models.DateTimeField(null=True, blank=True)
    attachment = models.FileField(
        help_text="Add Attachment to complete the Order",
        upload_to="attachments/",
        null=True,
        blank=True,
    )
    lab_user = models.ForeignKey(
        User,
        related_name="lab_orders",
        on_delete=models.SET_NULL,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_price(self):
        return sum([item.price for item in self.items.all()])

    def is_completed(self):
        if self.completed:
            return True
        return False

    def place_order(self):
        self.placed = timezone.now()
        self.save()
