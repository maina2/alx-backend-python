import django_filters
from .models import Message
class MessageFilter(django_filters.FilterSet):
    sent_at = django_filters.DateTimeFromToRangeFilter()
    sender = django_filters.NumberFilter(field_name='sender__user_id')
    recipient = django_filters.NumberFilter(field_name='recipient__user_id')

    class Meta:
        model = Message
        fields = ['conversation__conversation_id', 'sender', 'recipient', 'sent_at']
