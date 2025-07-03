from chats.models import User, Conversation, Message
from django.utils import timezone
from datetime import timedelta

# Create dummy users
user1, _ = User.objects.get_or_create(
    username='alice',
    defaults={
        'email': 'alice@example.com',
        'first_name': 'Alice',
        'last_name': 'Smith',
        'phone_number': '+12345678901',
    }
)
user2, _ = User.objects.get_or_create(
    username='bob',
    defaults={
        'email': 'bob@example.com',
        'first_name': 'Bob',
        'last_name': 'Jones',
        'phone_number': '+19876543210',
    }
)
user3, _ = User.objects.get_or_create(
    username='carol',
    defaults={
        'email': 'carol@example.com',
        'first_name': 'Carol',
        'last_name': 'White',
        'phone_number': '+11223344556',
    }
)
user4, _ = User.objects.get_or_create(
    username='dave',
    defaults={
        'email': 'dave@example.com',
        'first_name': 'Dave',
        'last_name': 'Brown',
        'phone_number': '+10987654321',
    }
)

# Create conversations
conv1, _ = Conversation.objects.get_or_create()
conv1.participants.set([user1, user2])
conv1.save()

conv2, _ = Conversation.objects.get_or_create()
conv2.participants.set([user2, user3, user4])
conv2.save()

conv3, _ = Conversation.objects.get_or_create()
conv3.participants.set([user1, user3])
conv3.save()

# Create messages for conv1
now = timezone.now()
Message.objects.get_or_create(
    conversation=conv1,
    sender=user1,
    recipient=user2,
    message_body="Hi Bob, this is Alice.",
    sent_at=now - timedelta(days=2)
)
Message.objects.get_or_create(
    conversation=conv1,
    sender=user2,
    recipient=user1,
    message_body="Hello Alice!",
    sent_at=now - timedelta(days=1, hours=2)
)

# Create messages for conv2
Message.objects.get_or_create(
    conversation=conv2,
    sender=user2,
    recipient=user3,
    message_body="Hey Carol, are you joining the meeting?",
    sent_at=now - timedelta(hours=5)
)
Message.objects.get_or_create(
    conversation=conv2,
    sender=user3,
    recipient=user4,
    message_body="Yes, I'll be there.",
    sent_at=now - timedelta(hours=4, minutes=30)
)
Message.objects.get_or_create(
    conversation=conv2,
    sender=user4,
    recipient=user2,
    message_body="Great, see you both soon.",
    sent_at=now - timedelta(hours=4)
)

# Create messages for conv3
Message.objects.get_or_create(
    conversation=conv3,
    sender=user1,
    recipient=user3,
    message_body="Carol, did you finish the report?",
    sent_at=now - timedelta(days=1)
)
Message.objects.get_or_create(
    conversation=conv3,
    sender=user3,
    recipient=user1,
    message_body="Yes, sent it this morning.",
    sent_at=now - timedelta(hours=3)
)

print("Dummy users, conversations, and messages created.")
print("User UUIDs:")
print("  Alice:", user1.user_id)
print("  Bob:", user2.user_id)
print("  Carol:", user3.user_id)
print("  Dave:", user4.user_id)
print("Conversation UUIDs:")
print("  conv1:", conv1.conversation_id)
print("  conv2:", conv2.conversation_id)
print("  conv3:", conv3.conversation_id)
print("Messages created for each conversation.")
