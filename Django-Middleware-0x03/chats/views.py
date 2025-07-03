from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status as drf_status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .pagination import MessagePagination
from .filters import MessageFilter

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on conversations.
    Supports filtering by participant user_id.
    """
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['participants__user_id']
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on messages.
    Supports filtering by conversation, sender, recipient, and sent_at range.
    """
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter
    pagination_class = MessagePagination
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        user = self.request.user
        # Only return messages where the user is a participant in the conversation
        return Message.objects.filter(
            conversation__participants__user=user
        ).order_by('-sent_at')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if not instance.conversation.participants.filter(user=user).exists():
            return Response({'detail': 'You do not have permission to view this message.'}, status=drf_status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if not instance.conversation.participants.filter(user=user).exists():
            return Response({'detail': 'You do not have permission to update this message.'}, status=drf_status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if not instance.conversation.participants.filter(user=user).exists():
            return Response({'detail': 'You do not have permission to delete this message.'}, status=drf_status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
