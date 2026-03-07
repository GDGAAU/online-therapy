import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from cloudinary.models import CloudinaryField


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)

        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    AUTH_PROVIDERS = (
        ("email", "Email"),
        ("google", "Google"),
    )

    auth_provider = models.CharField(
        max_length=20,
        choices=AUTH_PROVIDERS,
        default="email"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.username:
            # Generate username based on UUID
            self.username = f"user_{str(self.id)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username if self.username else f"user_{self.id}"


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    contact_info = models.CharField(
        max_length=255, blank=True, null=True)  # added
    profile_image = CloudinaryField(
        'image',
        folder='online_therapy/profile_image',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return f'{full_name} or {self.user.email}'
