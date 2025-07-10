# In messaging/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from vendors.models import Service # <-- Make sure this is imported
from .models import Conversation, Message
from .serializers import ConversationSerializer, ConversationDetailSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling conversations and messages.
    """
    permission_classes = [permissions.IsAuthenticated]
    # We will only allow listing, retrieving, and our custom creation/messaging.
    # We disable the default POST, PUT, DELETE.
    http_method_names = ['get', 'post', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationSerializer

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(Q(tourist=user) | Q(vendor=user)).prefetch_related('messages')

    # --- THIS IS THE CORRECTED METHOD ---
    def create(self, request, *args, **kwargs):
        """
        Overrides the default create method to handle conversation initiation.
        A tourist provides a service_id and an initial message body.
        """
        service_id = request.data.get('service_id')
        initial_body = request.data.get('body')

        if not service_id or not initial_body:
            return Response(
                {"error": "service_id and body are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = Service.objects.get(pk=service_id)
        except Service.DoesNotExist:
            return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

        if service.vendor.user == request.user:
            return Response(
                {"error": "You cannot start a conversation about your own service."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use get_or_create to prevent duplicate conversations
        conversation, created = Conversation.objects.get_or_create(
            service=service,
            tourist=request.user,
            vendor=service.vendor.user
        )
        
        # Create the first message for the conversation
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            body=initial_body
        )
        
        # Serialize the conversation object to return it in the response
        serializer = self.get_serializer(conversation)
        
        # The status code should be 201 Created if the conversation was new
        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        
        return Response(serializer.data, status=response_status)

    # This method is no longer needed as the logic is moved to `create`
    # def perform_create(self, serializer):
    #     pass 

    @action(detail=True, methods=['post'], url_path='messages')
    def send_message(self, request, pk=None):
        """
        Custom action to send a message to an existing conversation.
        """
        conversation = self.get_object()
        
        if request.user != conversation.tourist and request.user != conversation.vendor:
            return Response(
                {'error': 'You are not part of this conversation.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # We only need the 'body' for a new message
        body = request.data.get('body')
        if not body:
            return Response({'error': 'Message body cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            body=body
        )

        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)