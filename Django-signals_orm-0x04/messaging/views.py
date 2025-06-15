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