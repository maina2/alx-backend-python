from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    """
    nickname = serializers.CharField(required=False, allow_blank=True, max_length=30)
    full_name = serializers.SerializerMethodField()
    Serializer for the User model.

    Serializes user_id, username, email, first_name, last_name, phone_number, and is_active fields.
    Includes validation and update logic.
    """
    class Meta:
        model = User
        fields = [
            'user_id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'is_active',
        ]

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        qs = User.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(user_id=self.instance.user_id)
        if qs.exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if not value:
            raise serializers.ValidationError("Username is required.")
        qs = User.objects.filter(username=value)
        if self.instance:
            qs = qs.exclude(user_id=self.instance.user_id)
        if qs.exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_phone_number(self, value):
        if value:
            import re
            if not re.fullmatch(r'^\+?\d{7,15}$', value):
                raise serializers.ValidationError("Phone number must be 7-15 digits, optionally starting with '+'.")
        return value

    def validate_first_name(self, value):
        if value and len(value) > 50:
            raise serializers.ValidationError("First name must be 50 characters or fewer.")
        return value

    def validate_last_name(self, value):
        if value and len(value) > 50:
            raise serializers.ValidationError("Last name must be 50 characters or fewer.")
        return value

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            # Set unusable password if not provided
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        # Only update allowed fields
        for field in ['username', 'email', 'first_name', 'last_name', 'phone_number', 'is_active']:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        # Handle password update if provided
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.

    Serializes message_id, sender, recipient, conversation, message_body, and sent_at fields.
    Includes nested sender and recipient user details for read, and accepts user_ids for write.
    """
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    conversation = serializers.UUIDField(source='conversation.conversation_id', read_only=True)

    # Writable fields for creation/update
    sender_id = serializers.UUIDField(write_only=True, required=True)
    recipient_id = serializers.UUIDField(write_only=True, required=True)
    conversation_id = serializers.UUIDField(write_only=True, required=True)

    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'recipient',
            'conversation',
            'message_body',
            'sent_at',
            'sender_id',
            'recipient_id',
            'conversation_id',
        ]
        read_only_fields = ['message_id', 'sender', 'recipient', 'conversation', 'sent_at']

    def validate(self, attrs):
        # Validate sender
        sender_id = attrs.get('sender_id')
        recipient_id = attrs.get('recipient_id')
        conversation_id = attrs.get('conversation_id')
        if sender_id == recipient_id:
            raise serializers.ValidationError("Sender and recipient cannot be the same user.")
        try:
            sender = User.objects.get(user_id=sender_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Sender user_id is invalid.")
        try:
            recipient = User.objects.get(user_id=recipient_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Recipient user_id is invalid.")
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            raise serializers.ValidationError("Conversation ID is invalid.")
        # Check that both users are participants in the conversation
        if sender not in conversation.participants.all() or recipient not in conversation.participants.all():
            raise serializers.ValidationError("Both sender and recipient must be participants in the conversation.")
        return attrs

    def create(self, validated_data):
        sender_id = validated_data.pop('sender_id')
        recipient_id = validated_data.pop('recipient_id')
        conversation_id = validated_data.pop('conversation_id')
        sender = User.objects.get(user_id=sender_id)
        recipient = User.objects.get(user_id=recipient_id)
        conversation = Conversation.objects.get(conversation_id=conversation_id)
        message = Message.objects.create(
            sender=sender,
            recipient=recipient,
            conversation=conversation,
            **validated_data
        )
        return message

    def update(self, instance, validated_data):
        # Only allow updating message_body
        message_body = validated_data.get('message_body', None)
        if message_body is not None:
            instance.message_body = message_body
            instance.save()
        return instance


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.

    Serializes conversation_id, participants, created_at, and nested messages.
    Includes nested participants and messages for read, and accepts participants for write.
    """
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    # Writable field for creation/update
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'created_at',
            'messages',
            'participant_ids',
        ]
        read_only_fields = ['conversation_id', 'participants', 'created_at', 'messages']

    def validate_participant_ids(self, value):
        if not value or not isinstance(value, list):
            raise serializers.ValidationError("participant_ids must be a non-empty list of user_ids.")
        users = User.objects.filter(user_id__in=value)
        if users.count() != len(value):
            raise serializers.ValidationError("One or more user_ids are invalid.")
        return value

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        conversation = Conversation.objects.create()
        participants = User.objects.filter(user_id__in=participant_ids)
        conversation.participants.set(participants)
        conversation.save()
        return conversation

    def update(self, instance, validated_data):
        # Allow updating participants
        participant_ids = validated_data.get('participant_ids', None)
        if participant_ids is not None:
            participants = User.objects.filter(user_id__in=participant_ids)
            instance.participants.set(participants)
            instance.save()
        return instance
