# In vendors/serializers.py

from rest_framework import serializers
from .models import Vendor, Service, Booking

class VendorSerializer(serializers.ModelSerializer):
    """Serializer for vendor registration and viewing."""
    # To show the user's username in read-only mode
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Vendor
        fields = ['id', 'user', 'user_username', 'business_name', 'contact_phone', 'business_description', 'is_verified']
        # The 'user' field will be set automatically from the request, not sent by the user.
        read_only_fields = ['user', 'is_verified']

class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for managing services."""
    vendor = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Service
        fields = ['id', 'vendor', 'name', 'description', 'service_type', 'price', 'price_per', 'city', 'is_available']
        read_only_fields = ['vendor']

    def validate_vendor(self, value):
        """
        On validation, 'value' is the user. We need to get the vendor profile.
        This also checks if the user is a verified vendor.
        """
        try:
            vendor = value.vendor_profile
            if not vendor.is_verified:
                raise serializers.ValidationError("Your vendor account is not verified yet. Please wait for admin approval.")
            return vendor
        except Vendor.DoesNotExist:
            raise serializers.ValidationError("You do not have a vendor account. Please apply to become a vendor first.")
        

class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for tourists to create and view their bookings.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # To show service details in the response, not just the ID
    service = ServiceSerializer(read_only=True)
    # To accept a service ID when creating a booking
    service_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'service', 'service_id', 'booking_date', 
            'service_start_date', 'service_end_date', 'status', 'total_price'
        ]
        read_only_fields = ['status', 'total_price', 'booking_date']

    def create(self, validated_data):
        # We pop the service_id because the model field is 'service'
        service_id = validated_data.pop('service_id')
        service = Service.objects.get(pk=service_id)
        
        # Here you would typically calculate the total_price.
        # For now, we'll just use the service's base price.
        # A real implementation would consider dates, quantity etc.
        total_price = service.price

        # Create the booking instance
        booking = Booking.objects.create(
            service=service,
            total_price=total_price,
            **validated_data
        )
        return booking
