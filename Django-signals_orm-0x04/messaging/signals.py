from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory
from django_currentuser.middleware import get_current_user

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Creates a notification for the receiver when a new message is created.
    """
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Logs the old content of a message to MessageHistory before it is updated.
    """
    if instance.pk:  # Check if message exists (i.e., update operation)
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:  # Log only if content changed
                current_user = get_current_user()
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=current_user if current_user and current_user.is_authenticated else None
                )
                instance.edited = True  # Mark as edited
        except Message.DoesNotExist:
            pass  # New message, no history to log

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Deletes MessageHistory records where the user is the editor after user deletion.
    """
    MessageHistory.objects.filter(edited_by=instance).delete()