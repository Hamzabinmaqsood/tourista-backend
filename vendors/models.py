from django.db import models
from django.contrib.auth.models import User

class Vendor(models.Model):
    """
    Represents a local business or service provider.
    Each vendor is linked to a standard User account.
    """
    # This links the vendor profile to a user account.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=20)
    business_description = models.TextField(blank=True, null=True)
    # A simple flag for the admin to approve the vendor
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name

class Service(models.Model):
    """
    Represents a specific service offered by a vendor (e.g., a hotel room, a guided tour).
    """
    class ServiceType(models.TextChoices):
        HOTEL = 'HOTEL', 'Hotel'
        GUIDE = 'GUIDE', 'Tour Guide'
        TRANSPORT = 'TRANSPORT', 'Transportation'

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField()
    service_type = models.CharField(max_length=20, choices=ServiceType.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Provides context for the price, e.g., "per night", "per hour"
    price_per = models.CharField(max_length=50, default='per person')
    city = models.CharField(max_length=100)
    # A simple flag for the vendor to toggle availability
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} by {self.vendor.business_name}"
    
class Booking(models.Model):
    """
    Represents a booking made by a user for a specific service.
    """
    class BookingStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        COMPLETED = 'COMPLETED', 'Completed'

    # The user who made the booking
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    # The service that was booked
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    
    booking_date = models.DateTimeField(auto_now_add=True)
    # The date the service is for (e.g., hotel check-in date)
    service_start_date = models.DateField()
    service_end_date = models.DateField(null=True, blank=True, help_text="For multi-day services like hotels")
    
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Calculated at time of booking")
    
    class Meta:
        ordering = ['-booking_date']

    def __str__(self):
        return f"Booking by {self.user.username} for {self.service.name} on {self.service_start_date}"
