from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    dyslexia_severity = models.CharField(max_length=100, choices=[('mild', 'Mild'), ('moderate', 'Moderate'), ('severe', 'Severe')])
    
    def __str__(self) -> str:
        return self.full_name
# Create your models here.
