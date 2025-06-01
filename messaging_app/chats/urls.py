from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Explicitly using rest_framework.routers.DefaultRouter() for API routing
router = DefaultRouter()
router.register('conversations', ConversationViewSet, basename='conversations')
router.register('messages', MessageViewSet, basename='messages')

urlpatterns = [
    path('', include(router.urls)),
]