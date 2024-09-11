from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    dyslexia_severity = models.CharField(max_length=100, choices=[('mild', 'Mild'), ('moderate', 'Moderate'), ('severe', 'Severe')])
    
    def __str__(self) -> str:
        return self.full_name
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    reading_level = models.CharField(max_length=100, blank=True, null=True)
    preferred_font_size = models.PositiveIntegerField(default=14)
    background_color = models.CharField(max_length=7, default="#FFFFFF")
    learning_style = models.CharField(max_length=50, choices=[
        ('visual', 'Visual'),
        ('auditory', 'Auditory'),
        ('kinesthetic', 'Kinesthetic'),
    ], default='visual')
    
    def __str__(self):
        return self.user.username


# Create your models here.
