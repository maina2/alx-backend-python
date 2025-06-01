from django.urls import path, include
from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Explicitly using rest_framework.routers.DefaultRouter() for API routing
router = DefaultRouter()
router.register('conversations', ConversationViewSet, basename='conversations')

# Using rest_framework_nested.routers.NestedDefaultRouter for nested routes
nested_router = NestedDefaultRouter(router, 'conversations', lookup='conversation')
nested_router.register('messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(nested_router.urls)),
]