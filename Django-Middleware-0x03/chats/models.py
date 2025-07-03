from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Includes additional fields such as user_id (UUID), email, phone number, and status.
    """
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=80, blank=True, unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name =  models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=15, blank=True,null=True)
    is_active = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='chats_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='chats_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
    
    
    # Add any extra fields here that are not in AbstractUser
    # Example: phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        """
        Returns the string representation of the user (username).
        """
        return self.username

class Conversation(models.Model):
    """
    Model representing a conversation between multiple users.
    Each conversation has a unique ID and a set of participants.
    """
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField('User', related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the conversation using its ID.
        """
        return f"Conversation {self.conversation_id}"

class Message(models.Model):
    """
    Model representing a message sent within a conversation.
    Stores sender, recipient, conversation, message body, and timestamp.
    """
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey('User', related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey('User', related_name='received_messages', on_delete=models.CASCADE)
    conversation = models.ForeignKey('Conversation', related_name='messages', on_delete=models.CASCADE)
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the message, including sender and recipient.
        """
        return f"Message {self.message_id} from {self.sender} to {self.recipient}"
