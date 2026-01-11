from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import ListingViewSet, BookingViewSet

# Router for DRF ViewSets
router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    # Existing function-based endpoints 
    path("", views.listings_list, name="listings-list"),
    path("<int:pk>/", views.listing_detail, name="listing-detail"),

    # DRF API endpoints
    path("", include(router.urls)),
]



