from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Message

@login_required
def message_history(request, message_id):
    """
    Displays the edit history of a specific message.
    """
    message = get_object_or_404(Message, id=message_id)
    if request.user not in (message.sender, message.receiver):
        return render(request, 'messaging/error.html', {'error': 'You do not have permission to view this message.'})
    
    history = message.history.all()
    return render(request, 'messaging/message_history.html', {
        'message': message,
        'history': history
    })

@login_required
def delete_user(request):
    """
    Allows a user to delete their account after confirmation.
    """
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('login')  # Redirect to login page after deletion
    return render(request, 'messaging/delete_confirm.html')

@login_required
def conversation(request, user_id):
    """
    Displays threaded conversation between the current user and another user.
    """
    other_user = get_object_or_404(User, id=user_id)
    if request.user == other_user:
        return render(request, 'messaging/error.html', {'error': 'You cannot message yourself.'})

    # Fetch top-level messages (no parent) between the two users
    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user],
        parent_message__isnull=True
    ).select_related('sender', 'receiver').prefetch_related('replies__sender', 'replies__receiver', 'replies__replies')

    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        if content:
            parent_message = Message.objects.get(id=parent_id) if parent_id else None
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content,
                parent_message=parent_message
            )
            return redirect('messaging:conversation', user_id=user_id)

    return render(request, 'messaging/conversation.html', {
        'other_user': other_user,
        'messages': messages
    })

@login_required
def inbox(request):
    """
    Displays unread messages for the current user.
    """
    unread_messages = Message.unread.unread_for_user(request.user)
    if request.method == 'POST':
        message_id = request.POST.get('message_id')
        if message_id:
            message = get_object_or_404(Message, id=message_id, receiver=request.user)
            message.read = True
            message.save()
            return redirect('messaging:inbox')

    return render(request, 'messaging/inbox.html', {
        'unread_messages': unread_messages
    })