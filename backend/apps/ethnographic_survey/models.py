# ethnographic_survey/models.py
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

class EthnographicSurvey(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=20, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    occupation = models.CharField(max_length=100)
    village = models.CharField(max_length=255, blank=True, null=True)
    local_origin = models.CharField(max_length=50, choices=ANIOMA_LGAS, blank=True)
    location = models.CharField(max_length=100)
    cultural_practice = models.TextField()
    oral_history = models.TextField(blank=True, null=True)
    language_spoken = models.CharField(max_length=100)
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.location}"
