# In vendors/views.py
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from .models import Vendor, Service, Booking 
from .serializers import VendorSerializer, ServiceSerializer, BookingSerializer

class IsVerifiedVendor(permissions.BasePermission):
    """
    Custom permission to only allow verified vendors to manage services.
    """
    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user.is_authenticated:
            return False
        # The user must have a vendor profile and it must be verified
        try:
            return request.user.vendor_profile.is_verified
        except Vendor.DoesNotExist:
            return False

class VendorRegistrationView(generics.CreateAPIView):
    """
    API endpoint for users to apply to become a vendor.
    A user can only have one vendor application.
    """
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Check if user already has a vendor profile
        if Vendor.objects.filter(user=request.user).exists():
            return Response(
                {"error": "You have already submitted a vendor application."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Associate the vendor profile with the current logged-in user
        serializer.save(user=self.request.user)

class ServiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for verified vendors to manage their services.
    - list: View your services
    - create: Add a new service
    - retrieve: View a specific service
    - update: Edit a service
    - destroy: Delete a service
    """
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsVerifiedVendor]

    def get_queryset(self):
        """
        This view should only return services for the currently authenticated vendor.
        """
        return Service.objects.filter(vendor__user=self.request.user)

    def perform_create(self, serializer):
        # Associate the service with the vendor profile of the current user
        serializer.save(vendor=self.request.user.vendor_profile)

class TouristBookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for tourists to create and view their bookings.
    - list: View your past bookings.
    - create: Book a new service.
    - retrieve: View a specific booking detail.
    No update or delete is allowed for tourists through this simple endpoint.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options'] # Allow only safe methods + post

    def get_queryset(self):
        """
        Users can only see their own bookings.
        """
        return Booking.objects.filter(user=self.request.user).select_related('service__vendor')

    def perform_create(self, serializer):
        """
        Set the user for the booking to the current user.
        """
        serializer.save(user=self.request.user)

class VendorBookingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for VERIFIED VENDORS to view bookings for their services.
    - list: View all bookings for your services.
    - retrieve: View a specific booking's detail.
    - (Future) Can add actions to confirm or cancel bookings.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsVerifiedVendor] # Uses your existing permission

    def get_queryset(self):
        """
        Vendors can only see bookings for their own services.
        """
        # Get the vendor profile associated with the logged-in user
        vendor_profile = self.request.user.vendor_profile
        # Filter bookings where the service's vendor is the current vendor
        return Booking.objects.filter(service__vendor=vendor_profile)

