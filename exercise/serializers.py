from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from users_app.models import (Program, Session, Exercise, WorkoutCategory,
UserProgress, Meal, UserProgram)
from googletrans import Translator
translator = Translator()

def translate_field(instance, field_name, language):
    translated_field = f"{field_name}_{language}"
    if hasattr(instance, translated_field):
        return getattr(instance, translated_field) or getattr(instance, field_name)
    return getattr(instance, field_name)




# Program Serializer
class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = [
            'id', 'frequency_per_week', 'total_sessions',
            'program_goal', 'is_active'
        ]
        extra_kwargs = {
            'frequency_per_week': {'label': _("Frequency per Week")},
            'total_sessions': {'label': _("Total Sessions")},
            'program_goal': {'label': _("Program Goal")},
            'is_active': {'label': _("Is Active")},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        language = self.context.get('language', 'en')
        data['program_goal'] = translate_field(instance, 'program_goal', language)
        return data

# Session Serializer
class SessionSerializer(serializers.ModelSerializer):
    exercises = serializers.PrimaryKeyRelatedField(queryset=Exercise.objects.all(), many=True)
    meals = serializers.PrimaryKeyRelatedField(queryset=Meal.objects.all(), many=True)

    class Meta:
        model = Session
        fields = [
            'id', 'program', 'calories_burned',
            'session_number', 'session_time', 'exercises', 'meals'
        ]
        extra_kwargs = {
            'calories_burned': {'label': _("Calories Burned")},
            'session_time': {'label': _("Session Time")},
            'session_number': {'label': _("Session Number"), 'read_only': True},  # Read-only to ensure auto-assignment
            'exercises': {'label': _("Exercises")},
            'meals': {'label': _("Meals")},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Add more fields for translation or customization if necessary
        return data

    def create(self, validated_data):
        # Get the program from the validated data
        program = validated_data.get('program')

        # Determine the next session number for the program
        last_session = Session.objects.filter(program=program).order_by('-session_number').first()
        validated_data['session_number'] = (last_session.session_number + 1) if last_session else 1

        # Create and return the new session instance
        return super().create(validated_data)


# Exercise Serializer
class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = [
            'id', 'category', 'name', 'description', 'difficulty_level',
            'video_url', 'target_muscle', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'name': {'label': _("Exercise Name")},
            'description': {'label': _("Description")},
            'difficulty_level': {'label': _("Difficulty Level")},
            'video_url': {'label': _("Video URL")},
            'target_muscle': {'label': _("Target Muscle")},
            'created_at': {'label': _("Created At")},
            'updated_at': {'label': _("Updated At")},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        language = self.context.get('language', 'en')
        data['name'] = translate_field(instance, 'name', language)
        data['description'] = translate_field(instance, 'description', language)
        data['difficulty_level'] = translate_field(instance, 'difficulty_level', language)
        return data

# Workout Category Serializer
class WorkoutCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutCategory
        fields = ['id', 'category_name', 'description']
        extra_kwargs = {
            'category_name': {'label': _("Category Name")},
            'description': {'label': _("Description")},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        language = self.context.get('language', 'en')
        data['category_name'] = translate_field(instance, 'category_name', language)
        data['description'] = translate_field(instance, 'description', language)
        return data

# User Progress Serializer
from rest_framework import serializers

class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = [
            'id', 'user', 'date', 'completed_sessions', 'total_calories_burned',
            'calories_gained', 'missed_sessions', 'week_number', 'program'
        ]
        extra_kwargs = {
            'user': {'read_only': True},
            'date': {'label': "Date"},
            'completed_sessions': {'label': "Completed Sessions"},
            'total_calories_burned': {'label': "Calories Burned"},
            'calories_gained': {'label': "Calories Gained"},
            'missed_sessions': {'label': "Missed Sessions"},
            'week_number': {'label': "Week Number"},
            'program': {'label': "Program", 'read_only': True},
        }


# User Program Serializer
class UserProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgram
        fields = ['id', 'user', 'program', 'start_date', 'end_date', 'progress', 'is_active']
        extra_kwargs = {
            'user': {'read_only': True, 'label': _("User")},
            'program': {'label': _("Program")},
            'start_date': {'label': _("Start Date")},
            'end_date': {'label': _("End Date")},
            'progress': {'label': _("Progress")},
            'is_active': {'label': _("Is Active")},
        }

    def validate_program(self, value):
        user_goal = self.context['request'].user.goal
        if not value.is_active:
            raise serializers.ValidationError(_("Selected program is not relevant or is inactive."))
        return value



class UserProgramAllSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserProgram
        fields=['id','user','program','start_date','end_date','progress','is_active']



class UserUpdateProgressSerializer(serializers.Serializer):
    exercise_id = serializers.IntegerField(required=False, help_text="ID of the exercise")
    meal_id = serializers.IntegerField(required=False, help_text="ID of the meal")
    status = serializers.ChoiceField(
        choices=["completed", "skipped"],
        required=True,
        help_text="Status of the progress: 'completed' or 'skipped'"
    )

    def validate(self, data):
        if not data.get("exercise_id") and not data.get("meal_id"):
            raise serializers.ValidationError(
                "Either 'exercise_id' or 'meal_id' must be provided."
            )
        return data



class StartSessionSerializer(serializers.Serializer):
    session_id = serializers.IntegerField(required=True)

    def validate_session_id(self, value):
        # Session mavjudligini tekshirish
        if not Session.objects.filter(id=value).exists():
            raise serializers.ValidationError("Berilgan Session ID mavjud emas.")
        return value



class ProgressRequestSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["daily", "weekly"], required=True)
    date = serializers.DateField(required=True)