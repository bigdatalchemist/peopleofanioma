# apps/diaspora_tracker/models.py
from django.db import models

ANIOMA_LGAS = [
    ('Aniocha North', 'Aniocha North'),
    ('Aniocha South', 'Aniocha South'),
    ('Ndokwa East', 'Ndokwa East'),
    ('Ndokwa West', 'Ndokwa West'),
    ('Oshimili North', 'Oshimili North'),
    ('Oshimili South', 'Oshimili South'),
    ('Ukwuani', 'Ukwuani'),
    ('Ika North East', 'Ika North East'),
    ('Ika South', 'Ika South'),
]

class DiasporaEntry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    profession = models.CharField(max_length=100, blank=True)
    year_migrated = models.PositiveIntegerField(null=True, blank=True)
    
    local_origin = models.CharField(max_length=50, choices=ANIOMA_LGAS, blank=True)
    reason_for_migrating = models.TextField(blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.country})"
