
from django.db import models

class Listing(models.Model):
    """
    Represents a travel listing (hotel, villa, apartment, etc.).
    """

    # Core info
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)

    # Pricing & availability
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    available_from = models.DateField()
    available_to = models.DateField()

    # Image field 
    image = models.ImageField(upload_to='listings/', blank=True, null=True)

    # Meta info
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.location}"


# ----------------------------------------------------
# NEW PAYMENT MODEL ADDED
# ----------------------------------------------------

class Payment(models.Model):
    """
    Stores payment details for a booking made on a listing.
    """

    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"
