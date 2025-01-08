from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Instrument(models.Model):
    """Model for storing trading instrument data"""
    token = models.CharField(max_length=50)
    symbol = models.CharField(max_length=150)
    name = models.CharField(max_length=150, null=True, blank=True)
    expiry = models.CharField(max_length=50, null=True, blank=True)
    strike = models.FloatField(null=True, blank=True)
    lotsize = models.IntegerField(null=True, blank=True)
    instrumenttype = models.CharField(max_length=50, null=True, blank=True)
    exch_seg = models.CharField(max_length=10)
    tick_size = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now,  # Set default value
        editable=False  # Make it non-editable
    )
    updated_at = models.DateTimeField(
        auto_now=True  # This will still update on every save
    )

    class Meta:
        db_table = 'instruments'
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['token']),
            models.Index(fields=['exch_seg']),
        ]
        
    def __str__(self):
        return f"{self.symbol} ({self.instrumenttype})"