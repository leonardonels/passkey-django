from django.db import models
from users.models import User
from webauthn.helpers.structs import AuthenticatorTransport
import uuid, json, base64

# Create your models here.

class Credential(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credentials')
    id_bytes = models.BinaryField(unique=True, editable=False)
    credential_id = models.BinaryField()
    public_key = models.BinaryField()
    sign_counts = models.IntegerField()
    transports = models.CharField(max_length=255)

    def set_transports(self, transports):
        #enum list to str list
        enum_string_list = [transport.value for transport in transports]
        #str list to json
        enum_json_string = json.dumps(enum_string_list)
        #json to base64 to str
        self.transports = base64.b64encode(enum_json_string.encode('utf-8')).decode('utf-8')

        self.save()

    def get_transports(self):
        #str to base64 to json
        decoded_bytes = base64.b64decode(self.transports.encode('utf-8'))
        #decode json
        decoded_json_string = decoded_bytes.decode('utf-8')
        #json to str list
        enum_string_list = json.loads(decoded_json_string)
        #str list to enum list
        transports_enum_list = [AuthenticatorTransport(transport) for transport in enum_string_list]

        return transports_enum_list

    transports_list = property(get_transports, set_transports)

    def save(self, *args, **kwargs):
        if not self.id_bytes:
            self.id_bytes = uuid.uuid4().bytes
        return super().save(*args, **kwargs)
    
class TemporaryChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.challenge}"