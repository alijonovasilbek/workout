from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from .models import User
import re
from time import timezone
from users_app.models import User, Program

import logging

class RegisterSerializer(serializers.ModelSerializer):
    email_or_phone = serializers.CharField(label=_("Email or Phone"))
    password = serializers.CharField(write_only=True, label=_("Password"))
    goal = serializers.ChoiceField(
        choices=[],  # Populated dynamically in `__init__`
        label=_("Goal"),
        help_text=_("Select your goal"),
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email_or_phone', 'password',
            'gender', 'country', 'age', 'height', 'weight', 'goal', 'level'
        ]
        extra_kwargs = {
            'first_name': {'label': _("First Name")},
            'last_name': {'label': _("Last Name")},
            'gender': {'label': _("Gender")},
            'country': {'label': _("Country")},
            'age': {'label': _("Age")},
            'height': {'label': _("Height")},
            'weight': {'label': _("Weight")},
            'goal': {'label': _("Goal")},
            'level': {'label': _("Level")},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['goal'].choices = [
                (program.program_goal, program.program_goal)
                for program in Program.objects.all()
            ]
        except Exception as e:
            self.fields['goal'].choices = []
            logging.warning(f"Program choicesni yuklashda xato: {e}")

    def validate_goal(self, value):
        valid_goals = Program.objects.values_list('program_goal', flat=True)
        if value not in valid_goals:
            raise serializers.ValidationError(
                _("Noto'g'ri maqsad. Iltimos, quyidagilardan birini tanlang: ") + ", ".join(valid_goals)
            )
        return value

    def validate_email_or_phone(self, value):
        # Check if a user with the same email or phone already exists
        user = User.objects.filter(email_or_phone=value).first()
        if user:
            if user.is_active:
                raise serializers.ValidationError(_("This email or phone number is already registered."))
        return value

    def create(self, validated_data):
        # Extract and hash the password
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        return user

class VerifyCodeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(label=_("User ID"))
    code = serializers.IntegerField(label=_("Verification Code"))

    def validate_code(self, value):
        if not (1000 <= value <= 9999):  # Example range for a 4-digit code
            raise serializers.ValidationError(_("Verification code must be a 4-digit number."))
        return value


class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(max_length=255, label=_("Email or Phone"))
    password = serializers.CharField(write_only=True, label=_("Password"))


class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(max_length=255, label=_("Email or Phone"))

    def validate_email_or_phone(self, value):
        phone_regex = r'^\+998\d{9}$'
        if re.match(phone_regex, value):
            return value
        try:
            serializers.EmailField().run_validation(value)
            return value
        except serializers.ValidationError:
            raise serializers.ValidationError(_("Enter a valid phone number or email address."))


class ResetPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(max_length=255, label=_("Email or Phone"))
    verification_code = serializers.IntegerField(label=_("Verification Code"))
    new_password = serializers.CharField(write_only=True, max_length=128, label=_("New Password"))

    def validate_verification_code(self, value):
        if not (1000 <= value <= 9999):  # Adjust the range if needed
            raise serializers.ValidationError(_("Verification code must be a 4-digit number."))
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value










from users_app.models import User, Program, Session, Exercise, Meal, UserProgram

class ExerciseFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'description', 'difficulty_level', 'calories_burned', 'target_muscle']

class MealFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'meal_type', 'food_name', 'calories', 'water_content', 'preparation_time']

class SessionFullSerializer(serializers.ModelSerializer):
    exercises = ExerciseFullSerializer(many=True)
    meals = MealFullSerializer(many=True)
    
    class Meta:
        model = Session
        fields = ['id', 'scheduled_date', 'completion_status', 'calories_burned', 'session_time', 'exercises', 'meals']

class ProgramFullSerializer(serializers.ModelSerializer):
    sessions = SessionFullSerializer(many=True, source='session_set')
    
    class Meta:
        model = Program
        fields = ['id', 'program_goal', 'goal_type', 'frequency_per_week', 'total_sessions', 'is_active', 'sessions']

class UserProgramFullSerializer(serializers.ModelSerializer):
    program = ProgramFullSerializer()
    
    class Meta:
        model = UserProgram
        fields = ['id', 'start_date', 'end_date', 'progress', 'is_active', 'program']




from rest_framework import serializers

from users_app.models import UserProgram


class UserPaymentSerializer(serializers.ModelSerializer):
    """
    Order model serializer
    """
    class Meta:
        """
        Define the fields and their corresponding model fields
        """
        model = UserProgram
        fields = "__all__"



class ProgramSerializer(serializers.ModelSerializer):
    goal = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = ['id', 'goal', 'frequency_per_week', 'total_sessions']

    def get_goal(self, obj):
        language = self.context['request'].user.language
        return getattr(obj, f'program_goal_{language}')




class LanguageUpdateSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=[('uz', 'Uzbek'), ('ru', 'Russian'), ('en', 'English')])
