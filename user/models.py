from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

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
    

class TextContent(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
class Exercise(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    exercise_content = models.JSONField()
    difficulty_level = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='in_progress')  # e.g., "in_progress", "completed"
    score = models.FloatField(default=0.0)
    time_spent = models.DurationField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'exercise')
    
    def __str__(self):
        return f"{self.user.username} - {self.exercise.title}"


# Create your models here.