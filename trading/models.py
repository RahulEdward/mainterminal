from django.db import models

class Instrument(models.Model):
    token = models.CharField(max_length=50)
    symbol = models.CharField(max_length=150)
    name = models.CharField(max_length=150, null=True, blank=True)
    expiry = models.CharField(max_length=50, null=True, blank=True)
    strike = models.FloatField(null=True, blank=True)
    lotsize = models.IntegerField(null=True, blank=True)
    instrumenttype = models.CharField(max_length=50, null=True, blank=True)
    exch_seg = models.CharField(max_length=10)
    tick_size = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'instruments'

    def __str__(self):
        return f"{self.symbol} ({self.token})"
