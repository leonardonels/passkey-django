from django.contrib.auth.backends import BaseBackend
from users.models import User

class CustomAuthBackend(BaseBackend):
    def authenticate(self, user_credential):
        if user_credential:
            user=user_credential.user
            user.backend = 'web_auth.auth.CustomAuthBackend'
            user.save()
            return user
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None