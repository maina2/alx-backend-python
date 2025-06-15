from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification
from django.db.models.signals import post_save
from .signals import create_message_notification

class MessagingTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='testpass')
        self.receiver = User.objects.create_user(username='receiver', password='testpass')

    def test_message_creation(self):
        """Test that a message can be created."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this is a test message!"
        )
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.receiver, self.receiver)
        self.assertEqual(message.content, "Hello, this is a test message!")

    def test_notification_signal(self):
        """Test that a notification is created when a message is saved."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        notification = Notification.objects.get(user=self.receiver, message=message)
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)

    def test_no_notification_on_update(self):
        """Test that updating a message does not create a new notification."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original message"
        )
        initial_count = Notification.objects.count()
        message.content = "Updated message"
        message.save()
        self.assertEqual(Notification.objects.count(), initial_count)

    def test_signal_disconnection(self):
        """Test that disconnecting the signal prevents notification creation."""
        post_save.disconnect(create_message_notification, sender=Message)
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="No notification message"
        )
        self.assertFalse(Notification.objects.filter(user=self.receiver, message=message).exists())
        # Reconnect signal for other tests
        post_save.connect(create_message_notification, sender=Message)