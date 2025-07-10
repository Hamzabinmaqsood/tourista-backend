# In vendors/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VendorRegistrationView, ServiceViewSet,TouristBookingViewSet,VendorBookingViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')

router.register(r'bookings', TouristBookingViewSet, basename='tourist-booking')

# This router will now ONLY handle the vendor's services
service_router = DefaultRouter()
service_router.register(r'services', ServiceViewSet, basename='vendor-service')

# This router will handle the tourist's bookings
booking_router = DefaultRouter()
booking_router.register(r'bookings', TouristBookingViewSet, basename='tourist-booking')

urlpatterns = [
    path('register/', VendorRegistrationView.as_view(), name='vendor-register'),
    path('', include(router.urls)),
    # URLs for vendors to manage their own services
    path('my-services/', include(service_router.urls)),
    
    # URLs for tourists to create/view their bookings
    path('bookings/', include(booking_router.urls)),

    # New URL for vendors to view their received bookings
    path('my-bookings/', VendorBookingViewSet.as_view({'get': 'list'}), name='vendor-bookings-list'),
    path('my-bookings/<int:pk>/', VendorBookingViewSet.as_view({'get': 'retrieve'}), name='vendor-bookings-detail'),

]