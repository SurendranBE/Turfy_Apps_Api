from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"OTP for {self.user.email}: {self.otp}"
    

# Turfy Admin

class Turf(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)
    address = models.TextField()

    class Meta:
        db_table = 'turf'

    def __str__(self):
        return self.name

    @property
    def latitude_float(self):
        try:
            return float(self.latitude)
        except (ValueError, TypeError):
            return None

    @property
    def longitude_float(self):
        try:
            return float(self.longitude)
        except (ValueError, TypeError):
            return None
