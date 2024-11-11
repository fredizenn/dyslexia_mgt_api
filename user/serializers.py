from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from user.models import Exercise, Profile, Progress, TextContent

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Profile
        fields = ['user', 'reading_level', 'preferred_font_size', 'background_color', 'learning_style']
        
class TextContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextContent
        fields = '__all__'

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'
        
class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = ['id', 'user', 'exercise', 'status', 'score', 'time_spent', 'last_updated']
        read_only_fields = ['user']
        
    # def create(self, validated_data):
    #     user = self.context['request'].user
    #     return Progress.objects.create(user=user, **validated_data)
    
class ProgressReportSerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(source='exercise.title', read_only=True)
    
    class Meta:
        model = Progress
        fields = ['id', 'exercise_name', 'status', 'score', 'time_spent', 'last_updated']
