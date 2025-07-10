# In planner/serializers.py

from rest_framework import serializers
from .models import Itinerary, ItineraryItem, Destination 
from .models import CulturalEvent

class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        # Define the fields to include in the API response
        fields = ['id', 'name', 'description', 'city', 'country', 'destination_type', 'average_cost']



# In planner/serializers.py
# Keep the existing DestinationSerializer

from .models import Itinerary, ItineraryItem, Destination # Update imports

# ... (keep DestinationSerializer) ...

class ItineraryItemSerializer(serializers.ModelSerializer):
    """Serializer for an item within an itinerary (a specific destination on a specific day)."""
    # We want to show the full destination details, not just its ID.
    destination = DestinationSerializer(read_only=True)
    # We'll also accept a destination ID when creating a new item.
    destination_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ItineraryItem
        fields = ['id', 'destination', 'destination_id', 'day_number', 'start_time', 'end_time']


class ItinerarySerializer(serializers.ModelSerializer):
    """Serializer for listing and creating itineraries."""
    # This makes the user field read-only and sets it to the current user automatically.
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Itinerary
        fields = ['id', 'user', 'name', 'start_date', 'end_date', 'created_at']


class ItineraryDetailSerializer(ItinerarySerializer):
    """Serializer for viewing a single, detailed itinerary, including all its items."""
    items = ItineraryItemSerializer(many=True, read_only=True)

    class Meta(ItinerarySerializer.Meta):
        # Inherit fields from the base ItinerarySerializer and add 'items'
        fields = ItinerarySerializer.Meta.fields + ['items']


class CulturalEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CulturalEvent
        fields = ['id', 'name', 'description', 'city', 'start_date', 'end_date', 'category']