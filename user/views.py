# In a new file, e.g., users/views.py
from datetime import timedelta
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework_simplejwt.views import TokenObtainPairView
from user.models import Exercise, Profile, Progress, TextContent
from .serializers import CustomTokenObtainPairSerializer, ExerciseSerializer, ProfileSerializer, ProgressSerializer, TextContentSerializer
from django.shortcuts import get_object_or_404

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

@api_view(['POST'])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    # queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        try:
            return user.profile
        except Profile.DoesNotExist:
            # Optionally, create a profile if it doesn't exist:
            profile = Profile.objects.create(user=user)
            return profile
        
        
class TextContentListCreateView(generics.ListCreateAPIView):
    queryset = TextContent.objects.all()
    serializer_class = TextContentSerializer

class TextContentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TextContent.objects.all()
    serializer_class = TextContentSerializer
    
class ExerciseListCreateView(generics.ListCreateAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    
class ExerciseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer


class RetrieveProgressView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProgressSerializer
    

    def get_queryset(self):
        user = self.request.user
        return Progress.objects.filter(user=user)

class ProgressDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Progress.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProgressSerializer

class UpdateProgressView(generics.UpdateAPIView):
    serializer_class = ProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        exercise_id = request.data.get('exercise')
        time_spent_seconds = request.data.get('time_spent')

        if not exercise_id:
            return Response(
                {"detail": "Exercise ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not time_spent_seconds:
            return Response(
                {"detail": "Time spent is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            time_spent_seconds = int(time_spent_seconds)
        except ValueError:
            return Response(
                {"detail": "Time spent must be a valid integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        progress, created = Progress.objects.get_or_create(
            user=request.user,
            exercise_id=exercise_id,
            defaults={'time_spent': timedelta(seconds=0)}
        )

        progress.time_spent += timedelta(seconds=time_spent_seconds)

        serializer = self.get_serializer(progress, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)