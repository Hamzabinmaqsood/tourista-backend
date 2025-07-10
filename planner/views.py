from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .services import get_ai_recommendations
from .serializers import DestinationSerializer
from rest_framework import viewsets
from .models import Itinerary, ItineraryItem
from .serializers import ItinerarySerializer, ItineraryDetailSerializer, ItineraryItemSerializer
from .services import get_weather_alerts_for_itinerary

from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework import generics 
from .models import CulturalEvent 
from .serializers import CulturalEventSerializer 
from .services import get_optimized_route_for_itinerary

class AIRecommendationView(APIView):
    """
    API endpoint to get AI-powered destination recommendations.
    Requires authentication.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Handles GET request to provide destination suggestions.
        """
        user = request.user
        try:
            # The AI service needs the user's profile
            recommendations = get_ai_recommendations(user.profile)
            
            # If no recommendations are found, return a helpful message
            if not recommendations:
                return Response(
                    {"message": "Could not find recommendations matching your profile. Try adjusting your travel style or budget."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Serialize the data for the response
            serializer = DestinationSerializer(recommendations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            # Generic error handling
            return Response(
                {"error": "An unexpected error occurred.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ItineraryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to create, view, update, and delete their itineraries.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should only return itineraries for the currently authenticated user.
        """
        return Itinerary.objects.filter(user=self.request.user).prefetch_related('items__destination')

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the action.
        - Use ItineraryDetailSerializer for 'retrieve' (viewing one item).
        - Use ItinerarySerializer for all other actions (list, create, update).
        """
        if self.action == 'retrieve':
            return ItineraryDetailSerializer
        return ItinerarySerializer

    def perform_create(self, serializer):
        """
        Ensure the itinerary is saved with the current user.
        """
        serializer.save(user=self.request.user)

class ItineraryItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing items within a specific itinerary.
    Allows adding, updating, and removing destinations from a trip plan.
    """
    queryset = ItineraryItem.objects.all()
    serializer_class = ItineraryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter items to only those belonging to the itinerary specified in the URL.
        Also ensures the user owns the parent itinerary.
        """
        itinerary_id = self.kwargs['itinerary_pk']
        return ItineraryItem.objects.filter(
            itinerary__id=itinerary_id,
            itinerary__user=self.request.user # Security check!
        )

    def perform_create(self, serializer):
        """
        Automatically associate the new item with the itinerary from the URL.
        """
        itinerary_id = self.kwargs['itinerary_pk']
        itinerary = Itinerary.objects.get(id=itinerary_id, user=self.request.user) # Security check!
        serializer.save(itinerary=itinerary)

class WeatherAlertsView(APIView):
    """
    API endpoint to get weather alerts for a specific itinerary.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, itinerary_pk, *args, **kwargs):
        try:
            # Security check: ensure user owns the itinerary
            itinerary = Itinerary.objects.get(pk=itinerary_pk, user=request.user)
        except Itinerary.DoesNotExist:
            return Response({"error": "Itinerary not found."}, status=status.HTTP_404_NOT_FOUND)
            
        weather_alerts = get_weather_alerts_for_itinerary(itinerary)
        
        return Response(weather_alerts, status=status.HTTP_200_OK)

class CulturalEventsView(generics.ListAPIView):
    """
    API endpoint to list and filter cultural events.
    Allows filtering by city and category.
    Example: /api/planner/events/?city=Gilgit&category=SPORT
    """
    queryset = CulturalEvent.objects.all().order_by('start_date')
    serializer_class = CulturalEventSerializer
    permission_classes = [permissions.IsAuthenticated] # Keep it protected for now
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['city', 'category']

class ItineraryRouteView(APIView):
    """
    API endpoint to get an optimized route for a specific itinerary.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, itinerary_pk, *args, **kwargs):
        try:
            # Security check: ensure user owns the itinerary
            itinerary = Itinerary.objects.get(pk=itinerary_pk, user=request.user)
        except Itinerary.DoesNotExist:
            return Response({"error": "Itinerary not found."}, status=status.HTTP_404_NOT_FOUND)
            
        route_data = get_optimized_route_for_itinerary(itinerary)
        
        if "error" in route_data:
            # Pass along any errors from the service
            return Response(route_data, status=status.HTTP_400_BAD_REQUEST)

        return Response(route_data, status=status.HTTP_200_OK)
