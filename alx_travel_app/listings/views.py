from django.http import JsonResponse
from rest_framework import viewsets
from .models import Listing, Booking, Payment   # Payment added
from .serializers import ListingSerializer, BookingSerializer
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import uuid
from .tasks import send_booking_confirmation_email 


# Example view to list all listings
def listings_list(request):
    data = [
        {"id": 1, "name": "Beach House"},
        {"id": 2, "name": "Mountain Cabin"},
    ]
    return JsonResponse(data, safe=False)

# Example view to get a single listing by ID
def listing_detail(request, pk):
    # In real apps, you'd fetch from DB; here it's static for testing
    listings = {
        1: {"id": 1, "name": "Beach House"},
        2: {"id": 2, "name": "Mountain Cabin"},
    }
    listing = listings.get(pk)
    if listing:
        return JsonResponse(listing)
    return JsonResponse({"error": "Listing not found"}, status=404)


# API ViewSets required 
class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        booking = serializer.save()
        # Trigger async email task
        send_booking_confirmation_email.delay(
            booking.user.email,
            booking.id
        )


# ----------------------------------------------------
# NEW PAYMENT INTEGRATION (Chapa API)
# ----------------------------------------------------

@csrf_exempt
def initiate_payment(request, booking_id):
    """
    Initiates a payment request to Chapa and creates a Payment record.
    """
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return JsonResponse({"error": "Booking not found"}, status=404)

    transaction_id = str(uuid.uuid4())

    payload = {
        "amount": float(booking.total_amount),
        "currency": "ETB",
        "email": booking.user.email,
        "tx_ref": transaction_id,
        "callback_url": "https://yourdomain.com/api/verify-payment/"
    }

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }

    chapa_url = "https://api.chapa.co/v1/transaction/initialize"
    response = requests.post(chapa_url, json=payload, headers=headers)

    data = response.json()

    # Create Payment entry
    Payment.objects.create(
        transaction_id=transaction_id,
        amount=booking.total_amount,
        status="Pending"
    )

    return JsonResponse(data)


@csrf_exempt
def verify_payment(request, transaction_id):
    """
    Verifies a payment with Chapa using transaction ID.
    """
    try:
        payment = Payment.objects.get(transaction_id=transaction_id)
    except Payment.DoesNotExist:
        return JsonResponse({"error": "Payment not found"}, status=404)

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }

    chapa_verify_url = f"https://api.chapa.co/v1/transaction/verify/{transaction_id}"
    response = requests.get(chapa_verify_url, headers=headers)
    data = response.json()

    # Update payment status
    if data.get("status") == "success":
        payment.status = "Completed"
    else:
        payment.status = "Failed"

    payment.save()

    return JsonResponse({"payment_status": payment.status})
