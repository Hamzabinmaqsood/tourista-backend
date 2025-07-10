# In messaging/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conversation, Message
from vendors.models import Service

class MessageSerializer(serializers.ModelSerializer):
    """Serializer for a single message."""
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_username', 'body', 'timestamp']
        read_only_fields = ['id', 'sender', 'sender_username', 'timestamp']

class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for listing conversations."""
    tourist_username = serializers.CharField(source='tourist.username', read_only=True)
    vendor_username = serializers.CharField(source='vendor.username', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'service', 'service_name', 'tourist', 'tourist_username', 
            'vendor', 'vendor_username', 'last_message', 'updated_at'
        ]

    def get_last_message(self, obj):
        """Returns the body of the most recent message in the conversation."""
        last_msg = obj.messages.order_by('-timestamp').first()
        return last_msg.body if last_msg else None

class ConversationDetailSerializer(ConversationSerializer):
    """Serializer for viewing a single conversation with all its messages."""
    messages = MessageSerializer(many=True, read_only=True)

    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['messages']