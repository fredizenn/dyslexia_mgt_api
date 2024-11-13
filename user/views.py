# In a new file, e.g., users/views.py
from datetime import timedelta

from django.http import JsonResponse
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
from user.utils import get_next_difficulty, suggest_exercises
from .serializers import CustomTokenObtainPairSerializer, ExerciseSerializer, ProfileSerializer, ProgressReportSerializer, ProgressSerializer, TextContentSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from google.cloud import speech
from fuzzywuzzy import fuzz

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="A user with this email already exists.")]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="A user with this username already exists.")]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def create(self, validated_data):
        # Check for existing users with the same email or username
        if User.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})

        if User.objects.filter(username=validated_data['username']).exists():
            raise serializers.ValidationError({"username": "A user with this username already exists."})

        # Create new user if validation passes
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def to_representation(self, instance):
        return {
            "success": True,
            "message": "User registered successfully.",
            "user": {
                "username": instance.username,
                "email": instance.email,
                "first_name": instance.first_name,
                "last_name": instance.last_name
            }
        }

@api_view(['POST'])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            token_data = serializer.validated_data
            
            response_data = {
                'data': {
                    'token': token_data['access'],
                    'refresh_token': token_data['refresh'],
                },
                'success': True,
                'message': "Logged in successfully"
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'data': None,
                'success': False,
                'message': "Authentication failed: " + str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        try:
            return user.profile  
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user)
            return profile

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance) 
        response_data = {
            'data': {
                'profile': serializer.data
            },
            'success': True,
            'message': "Profile retrieved successfully"
        }
        return Response(response_data, status=status.HTTP_200_OK)

class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request
        try:
            return user
        except User.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = {
            'data': {
                'current_user': serializer.data
            },
            'success': True,
            'message': "Current user retrieved successfully"
        }
        return Response(response_data, status=status.HTTP_200_OK)
        
        
class TextContentListCreateView(generics.ListCreateAPIView):
    queryset = TextContent.objects.all()
    serializer_class = TextContentSerializer

class TextContentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TextContent.objects.all()
    serializer_class = TextContentSerializer
    
class ExerciseListCreateView(generics.ListCreateAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

    def get(self, request, *args, **kwargs):
        exercises = self.get_queryset()
        serializer = self.get_serializer(exercises, many=True)

        response_data = {
            'data': serializer.data,
            'success': True,
            'message': 'Exercise list retrieved successfully'
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            response_data = {
                'data': serializer.data,
                'success': True,
                'message': 'Exercise created successfully'
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'data': None,
                'success': False,
                'message': 'Exercise creation failed: ' + str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
class ExerciseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

    def get(self, request, *args, **kwargs):
        try:
            exercise = self.get_object()
            serializer = self.get_serializer(exercise)
            response_data = {
                'data': serializer.data,
                'success': True,
                'message': 'Exercise retrieved successfully'
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'data': None,
                'success': False,
                'message': 'Failed to retrieve exercise: ' + str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            exercise = self.get_object()
            serializer = self.get_serializer(exercise, data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            response_data = {
                'data': serializer.data,  # Updated exercise data
                'success': True,
                'message': 'Exercise updated successfully'
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'data': None,
                'success': False,
                'message': 'Failed to update exercise: ' + str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            exercise = self.get_object()
            self.perform_destroy(exercise)
            response_data = {
                'data': None,
                'success': True,
                'message': 'Exercise deleted successfully'
            }
            return Response(response_data, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'data': None,
                'success': False,
                'message': 'Failed to delete exercise: ' + str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


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

class ProgressReportView(generics.ListAPIView):
    serializer_class = ProgressReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Progress.objects.filter(user=self.request.user)
    

class ProgressHistoryView(generics.ListAPIView):
    serializer_class = ProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Progress.objects.filter(user=user)

        # Optional filters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        exercise_id = self.request.query_params.get('exercise')

        if start_date and end_date:
            queryset = queryset.filter(last_updated__range=[start_date, end_date])
        if exercise_id:
            queryset = queryset.filter(exercise_id=exercise_id)

        return queryset
    
class ProgressSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        progress_entries = Progress.objects.filter(user=user)

        total_exercises = progress_entries.count()
        completed_exercises = progress_entries.filter(status="completed").count()
        average_score = progress_entries.aggregate(Avg('score'))['score__avg']
        average_time_spent = progress_entries.aggregate(Avg('time_spent'))['time_spent__avg']

        summary_data = {
            "total_exercises": total_exercises,
            "completed_exercises": completed_exercises,
            "average_score": average_score,
            "average_time_spent": average_time_spent,
        }

        return Response(summary_data, status=200)

class NextExerciseView(generics.RetrieveAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        difficulty_level = get_next_difficulty(user)
        next_exercise = Exercise.objects.filter(difficulty_level=difficulty_level).order_by('?').first()  # Random exercise
        
        if next_exercise:
            serializer = self.get_serializer(next_exercise)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "No exercises available."}, status=status.HTTP_404_NOT_FOUND)
    
class SpeechToTextView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        
        if 'audio' not in request.FILES:
            return Response({"detail": "No audio file provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        audio_file = request.FILES['audio'].read()
        
        client = speech.SpeechClient()
        
        audio = speech.RecognitionAudio(content=audio_file)
        config = speech.RecognitionConfig(
            encoding = speech.RecognitionConfig.AudioEncoding.MP3 | speech.RecognitionConfig.AudioEncoding.LINEAR16 | speech.RecognitionConfig.AudioEncoding.OGG_OPUS | speech.RecognitionConfig.AudioEncoding.FLAC,
            # sample_rate_hertz = 16000,
            language_code = 'en-GH',
        )
        
        try:
            response = client.recognize(config=config, audio=audio)
            
            transcriptions = [result.alternatives[0].transcript for result in response.results]
            return Response({"transcriptions": transcriptions}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class MatchAnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        actual_answer = request.data.get('actual_answer')
        user_answer = request.data.get('user_answer')

        if not actual_answer or not user_answer:
            return JsonResponse({"error": "Both 'actual_answer' and 'user_answer' are required."}, status=400)
        
        match_score = fuzz.ratio(actual_answer, user_answer)
        
        if match_score >= 80:
            return Response({"success": True, "message": "Matching completed with a score of " + str(match_score) + "%", "match_score": match_score, "match": True})
        else:
            return Response({"success": False, "message": "Matching completed with a score of " + str(match_score) + "%", "match_score": match_score, "match": False})

class SuggestedExerciseView(generics.RetrieveAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        next_exercises = suggest_exercises(user)
        # next_exercise = Exercise.objects.filter(difficulty_level=difficulty_level).order_by('?').first()  # Random exercise
        
        if next_exercises:
            serializer = self.get_serializer(next_exercises)
            return Response(next_exercises, status=status.HTTP_200_OK)
        return Response({"detail": "No exercises available."}, status=status.HTTP_404_NOT_FOUND)        