# In messaging/models.py

from django.db import models
from django.contrib.auth.models import User
from vendors.models import Service

class Conversation(models.Model):
    """
    Represents a conversation between a user (tourist) and a vendor
    about a specific service.
    """
    # The service this conversation is about
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='conversations')
    # The user who initiated the conversation (the tourist)
    tourist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiated_conversations')
    # The vendor who owns the service
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_conversations')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensure only one conversation exists between a tourist and a vendor for a specific service
        unique_together = ('service', 'tourist', 'vendor')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation about '{self.service.name}' between {self.tourist.username} and {self.vendor.username}"


class Message(models.Model):
    """
    Represents a single message within a conversation.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    # The user who sent this message (can be tourist or vendor)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    # The actual message content
    body = models.TextField()
    
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"