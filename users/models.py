from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    client_id = models.CharField(max_length=100, unique=True)
    api_key = models.BinaryField(max_length=500)  # Changed to BinaryField for encrypted storage
    access_token = models.BinaryField(max_length=500, null=True, blank=True)  
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.username} ({self.client_id})"

    @staticmethod
    def get_encryption_key():
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=settings.SECRET_KEY.encode()[:16],
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
        return Fernet(key)

    def set_api_key(self, api_key):
        f = self.get_encryption_key()
        self.api_key = f.encrypt(api_key.encode())

    def get_api_key(self):
        if not self.api_key:
            return None
        f = self.get_encryption_key()
        return f.decrypt(self.api_key).decode()

    def set_access_token(self, token):
        if token is None:
            self.access_token = None
        else:
            f = self.get_encryption_key()
            self.access_token = f.encrypt(token.encode())

    def get_access_token(self):
        if not self.access_token:
            return None
        f = self.get_encryption_key()
        return f.decrypt(self.access_token).decode()