from django.contrib import admin
from .models import Vendor, Service

class ServiceInline(admin.TabularInline):
    """Allows editing services directly from the vendor's admin page."""
    model = Service
    extra = 1 # Show one extra blank form for a new service

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    """Admin view for Vendors."""
    list_display = ('business_name', 'user', 'contact_phone', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('business_name', 'user__username')
    inlines = [ServiceInline]

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin view for Services."""
    list_display = ('name', 'vendor', 'service_type', 'city', 'price', 'is_available')
    list_filter = ('service_type', 'city', 'is_available')
    search_fields = ('name', 'description', 'vendor__business_name')