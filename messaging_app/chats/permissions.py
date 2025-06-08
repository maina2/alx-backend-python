from rest_framework import permissions
from rest_framework.permissions import BasePermission
from .models import Message, Conversation

class IsParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Message):
            return obj.user == request.user or obj.conversation.participants.filter(id=request.user.id).exists()
        if isinstance(obj, Conversation):
            return obj.participants.filter(id=request.user.id).exists()
        return False