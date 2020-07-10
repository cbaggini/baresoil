from django.contrib.gis import admin
from .models import PreviousQueries

admin.site.register(PreviousQueries, admin.OSMGeoAdmin)