from django.contrib.gis.db import models
from django.utils import timezone

class PreviousQueries(models.Model):
    mnth = models.IntegerField()
    yr = models.IntegerField()
    ndvi = models.FloatField()
    ndvi_low = models.FloatField()
    request_datetime = models.DateTimeField(default=timezone.now, blank=True)
    nelat = models.FloatField()
    nelng = models.FloatField()
    swlat = models.FloatField()
    swlng = models.FloatField()



