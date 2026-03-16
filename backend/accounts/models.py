from django.db import models
from django.contrib.auth.hashers import make_password
from .utils.encryption import encrypt_value, decrypt_value


class User(models.Model):

    username = models.CharField(max_length=100)

    email = models.EmailField(unique=True)

    password = models.TextField()

    client_id = models.CharField(max_length=255, unique=True)

    secret_key = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        # Hash password if not hashed
        if not self.password.startswith("pbkdf2"):
            self.password = make_password(self.password)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class AccessToken(models.Model):

    client_id = models.CharField(
        max_length=255,
        db_index=True
    )

    access_token = models.TextField()

    token_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("client_id", "token_date")
        indexes = [
            models.Index(fields=["client_id", "token_date"])
        ]

    def save(self, *args, **kwargs):

        # Prevent double encryption
        if self.access_token and not self.access_token.startswith("gAAAA"):
            self.access_token = encrypt_value(self.access_token)

        super().save(*args, **kwargs)

    def get_token(self):

        if not self.access_token:
            return None

        return decrypt_value(self.access_token)

    def __str__(self):

        return f"{self.client_id} - {self.token_date}"


class FyersAccount(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    client_id = models.CharField(max_length=100)

    secret_key = models.CharField(max_length=200)

    redirect_uri = models.CharField(max_length=200)

    access_token = models.TextField(blank=True, null=True)

    token_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.client_id


from django.db import models


class BhavcopyFile(models.Model):

    file_name = models.CharField(max_length=200, unique=True)

    trade_date = models.DateField()

    year = models.IntegerField()

    month = models.CharField(max_length=10)

    file_data = models.BinaryField()

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.file_name


class DownloadLog(models.Model):

    file_name = models.CharField(max_length=200, unique=True)

    trade_date = models.DateField(null=True, blank=True)

    week_day = models.CharField(max_length=20)

    status = models.CharField(max_length=20)

    download_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_name


class GeneratedFile(models.Model):

    file_name = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)

    file_data = models.BinaryField()