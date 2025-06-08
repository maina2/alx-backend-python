from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipant
from .filters import MessageFilter

class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsParticipant]
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['participants']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsParticipant]
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_id')
        if conversation_id:
            if not Conversation.objects.filter(id=conversation_id, participants=self.request.user).exists():
                return Response({"detail": "Not a participant"}, status=status.HTTP_403_FORBIDDEN)
            return Message.objects.filter(conversation_id=conversation_id)
        return Message.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get('conversation_id')
        if not Conversation.objects.filter(id=conversation_id, participants=request.user).exists():
            return Response({"detail": "Not a participant"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)