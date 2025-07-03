from rest_framework import permissions 

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access messages.
    - Only authenticated users can access the API.
    - Only participants in a conversation can send, view, update, and delete messages.
    """

    def has_permission(self, request, view):
        # Only allow authenticated users
        if not request.user or not request.user.is_authenticated:
            return False

        # For ConversationViewSet, allow all authenticated users to list/retrieve conversations
        if view.basename == 'conversation':
            return True

        # For MessageViewSet, allow only for safe methods, otherwise defer to has_object_permission
        if view.basename == 'message':
            if request.method in permissions.SAFE_METHODS:
                return True
            # For PUT, PATCH, DELETE, POST, defer to object-level permission
            return True

        return False

    def has_object_permission(self, request, view, obj):
        # Only allow participants of the conversation to access the message/conversation
        user = request.user

        # For ConversationViewSet, check if user is a participant
        if view.basename == 'conversation':
            return obj.participants.filter(user=user).exists()

        # For MessageViewSet, check if user is a participant in the related conversation
        if view.basename == 'message':
            if hasattr(obj, 'conversation'):
                is_participant = obj.conversation.participants.filter(user=user).exists()
                if request.method in ['PUT', 'PATCH', 'DELETE']:
                    return is_participant
                # For safe methods (GET, HEAD, OPTIONS), allow if participant
                return is_participant
        return False
