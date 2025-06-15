from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory
from django.db.models.signals import post_save, pre_save, post_delete
from .signals import create_message_notification, log_message_edit, cleanup_user_data

class MessagingTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='testpass')
        self.receiver = User.objects.create_user(username='receiver', password='testpass')
        self.editor = User.objects.create_user(username='editor', password='testpass')

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
        self.assertFalse(message.edited)
        self.assertIsNone(message.parent_message)
        self.assertFalse(message.read)

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
        """Test that disconnecting the notification signal prevents notification creation."""
        post_save.disconnect(create_message_notification, sender=Message)
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="No notification message"
        )
        self.assertFalse(Notification.objects.filter(user=self.receiver, message=message).exists())
        post_save.connect(create_message_notification, sender=Message)

    def test_message_edit_logging(self):
        """Test that editing a message logs the old content and editor in MessageHistory."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original message"
        )
        self.client.login(username='editor', password='testpass')
        message.content = "Updated message"
        message.save()
        history = MessageHistory.objects.get(message=message)
        self.assertEqual(history.old_content, "Original message")
        self.assertEqual(history.edited_by, self.editor)
        self.assertTrue(message.edited)

    def test_no_history_on_create(self):
        """Test that creating a message does not create a MessageHistory entry."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="New message"
        )
        self.assertFalse(MessageHistory.objects.filter(message=message).exists())
        self.assertFalse(message.edited)

    def test_no_history_on_same_content(self):
        """Test that updating with same content does not create a MessageHistory entry."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Same message"
        )
        message.content = "Same message"
        message.save()
        self.assertFalse(MessageHistory.objects.filter(message=message).exists())
        self.assertFalse(message.edited)

    def test_edit_signal_disconnection(self):
        """Test that disconnecting the edit signal prevents history logging."""
        pre_save.disconnect(log_message_edit, sender=Message)
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original message"
        )
        message.content = "Updated message"
        message.save()
        self.assertFalse(MessageHistory.objects.filter(message=message).exists())
        self.assertFalse(message.edited)
        pre_save.connect(log_message_edit, sender=Message)

    def test_user_deletion_cleanup(self):
        """Test that deleting a user removes related messages, notifications, and message histories."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        self.client.login(username='editor', password='testpass')
        message.content = "Updated message"
        message.save()
        self.assertTrue(Notification.objects.filter(user=self.receiver, message=message).exists())
        self.assertTrue(MessageHistory.objects.filter(message=message, edited_by=self.editor).exists())
        
        self.sender.delete()
        self.assertFalse(Message.objects.filter(sender=self.sender).exists())
        self.assertFalse(Notification.objects.filter(message=message).exists())
        self.assertFalse(MessageHistory.objects.filter(edited_by=self.editor).exists())

    def test_threaded_message_creation(self):
        """Test that a reply can be created with parent_message."""
        parent = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Parent message"
        )
        reply = Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content="Reply message",
            parent_message=parent
        )
        self.assertEqual(reply.parent_message, parent)
        self.assertIn(reply, parent.replies.all())

    def test_threaded_replies_fetch(self):
        """Test that threaded replies are fetched efficiently."""
        parent = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Parent message"
        )
        reply1 = Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content="Reply 1",
            parent_message=parent
        )
        reply2 = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Reply to Reply 1",
            parent_message=reply1
        )
        with self.assertNumQueries(2):  # One for parent, one for all replies
            threaded_replies = parent.get_threaded_replies()
            self.assertIn(reply1, threaded_replies)
            self.assertIn(reply2, reply1.replies.all())

    def test_unread_messages_manager(self):
        """Test that UnreadMessagesManager filters unread messages for a user."""
        message1 = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Unread message",
            read=False
        )
        message2 = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Read message",
            read=True
        )
        unread = Message.unread.unread_for_user(self.receiver)
        self.assertIn(message1, unread)
        self.assertNotIn(message2, unread)
        self.assertEqual(unread.count(), 1)

    def test_unread_manager_optimization(self):
        """Test that UnreadMessagesManager uses .only() for optimization."""
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Unread message",
            read=False
        )
        with self.assertNumQueries(1):
            unread = Message.unread.unread_for_user(self.receiver)
            # Accessing fields specified in .only()
            for msg in unread:
                self.assertIsNotNone(msg.id)
                self.assertIsNotNone(msg.sender.username)
                self.assertIsNotNone(msg.content)