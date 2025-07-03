from datetime import datetime, time, timedelta
import logging
import os
from django.http import HttpResponseForbidden, HttpResponseTooManyRequests
from django.core.cache import cache

# Configure logging to file
logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'requests.log'),
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.limit = 5  # 5 messages per minute
        self.window = timedelta(minutes=1)

    def __call__(self, request):
        if request.method == 'POST' and 'messages' in request.path:
            ip = request.META.get('REMOTE_ADDR')
            cache_key = f'message_limit_{ip}'
            
            # Get current count and timestamp
            count, timestamp = cache.get(cache_key, (0, datetime.now()))
            
            # Reset if window has passed
            if datetime.now() - timestamp > self.window:
                count = 0
                timestamp = datetime.now()
            
            # Check limit
            if count >= self.limit:
                return HttpResponseTooManyRequests("Rate limit exceeded: 5 messages per minute")
            
            # Update count
            cache.set(cache_key, (count + 1, timestamp), 60)  # Store for 60 seconds
            
        return self.get_response(request)


class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for admin or moderator access on specific actions
        if request.method in ['DELETE'] and 'admin' in request.path:
            user = request.user
            if not user.is_authenticated or not (user.is_staff or user.is_superuser):
                return HttpResponseForbidden("Access denied: Admin or moderator privileges required")
        
        return self.get_response(request)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the request details
        user = request.user if hasattr(request, 'user') else 'Anonymous'
        logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_time = datetime.now().time()
        # Restrict access between 9PM (21:00) and 6AM (06:00)
        if time(21, 0) <= current_time or current_time <= time(6, 0):
            return HttpResponseForbidden("Access denied: Service unavailable during these hours (9PM-6AM)")
        
        return self.get_response(request)
