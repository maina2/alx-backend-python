from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        auth = super().authenticate(request)
        if auth is not None:
            user, token = auth
            return user, token
        return None