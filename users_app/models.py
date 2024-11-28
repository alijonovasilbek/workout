from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from googletrans import Translator
from django.utils import timezone
from rest_framework import status
from rest_framework import status
from django.utils.timezone import now
from datetime import timedelta
from threading import Timer

translator = Translator()


def translate_text(text, target_language):
    try:
        translation = translator.translate(text, dest=target_language)
        return translation.text if translation else text
    except Exception as e:
        print(f"Translation error: {e}")
        return text


# Default function for notification_preferences
def default_notification_preferences():
    return {
        "email": True,
        "sms": False,
        "in_app": True,
        "reminder_enabled": True
    }


# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email_or_phone, password=None, **extra_fields):
        if not email_or_phone:
            raise ValueError("The Email or Phone must be set")

        # Ensure all required fields have valid defaults or raise errors
        extra_fields.setdefault('first_name', 'Admin')
        extra_fields.setdefault('last_name', 'User')
        extra_fields.setdefault('age', 30)  # Default age for admin
        extra_fields.setdefault('height', 170)  # Default height
        extra_fields.setdefault('weight', 70)  # Default weight
        extra_fields.setdefault('goal', 'General Fitness')
        extra_fields.setdefault('level', 'Intermediate')
        extra_fields.setdefault('photo', 'default_photo.jpg')  # Default photo path

        user = self.model(email_or_phone=email_or_phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email_or_phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email_or_phone, password, **extra_fields)


# User Model
class User(AbstractBaseUser, PermissionsMixin):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ru', 'Russian'),
        ('uz', 'Uzbek'),
    ]

    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    email_or_phone = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=128)
    date_joined = models.DateTimeField(default=now, verbose_name="Date Joined")  # Yangi maydon

    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=False, null=False)
    country = models.CharField(max_length=50, blank=False, choices=[('Uzbekistan', 'Uzbekistan'), ('Russia', 'Russia'), ('Kazakhstan', 'Kazakhstan'), ('Other', 'Other')], default='Other')
    notification_preferences = models.JSONField(default=default_notification_preferences)
    reminder_time = models.TimeField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=False, null=False, validators=[MinValueValidator(16), MaxValueValidator(50)])
    height = models.PositiveIntegerField(blank=False, null=False,
                                         validators=[MinValueValidator(140), MaxValueValidator(220)])
    weight = models.PositiveIntegerField(blank=False, null=False,
                                         validators=[MinValueValidator(30), MaxValueValidator(200)])
    goal = models.CharField(max_length=255, blank=False, null=False)
    level = models.CharField(max_length=50, blank=False, null=False)
    is_premium = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='user_photos/', blank=False, null=False)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')


    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email_or_phone'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email_or_phone


# User Progress Model
class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    completed_sessions = models.IntegerField(default=0)
    total_calories_burned = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    calories_gained = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    missed_sessions = models.IntegerField(default=0)
    week_number = models.IntegerField()
    program = models.ForeignKey('Program', on_delete=models.CASCADE)  # Link to the program for tracking


# Program Model
class Program(models.Model):
    frequency_per_week = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)])
    total_sessions = models.IntegerField(default=0)  # Number of sessions in the program
    program_goal = models.CharField(max_length=255)
    program_goal_uz = models.CharField(max_length=255, blank=True, null=True)
    program_goal_ru = models.CharField(max_length=255, blank=True, null=True)
    program_goal_en = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.program_goal_uz:
            self.program_goal_uz = translate_text(self.program_goal, 'uz')
        if not self.program_goal_ru:
            self.program_goal_ru = translate_text(self.program_goal, 'ru')
        if not self.program_goal_en:
            self.program_goal_en = translate_text(self.program_goal, 'en')
        super(Program, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.program_goal} "

    def increment_progress(self):
        """Increment the progress by 1, until it reaches total_sessions."""
        if self.progress < self.total_sessions:
            self.progress += 1
            self.save()
        if self.progress == self.total_sessions:
            self.is_active = False
            self.save()


class UserProgram(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_programs")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="user_programs")
    start_date = models.DateField()
    end_date = models.DateField(null=False, blank=False)
    progress = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    total_amount = models.IntegerField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=255)

    def calculate_progress(self):
        total_sessions = self.program.total_sessions
        completed_sessions = SessionCompletion.objects.filter(
            user=self.user,
            session__program=self.program,
            is_completed=True
        ).count()
        return (completed_sessions / total_sessions) * 100 if total_sessions > 0 else 0

    def __str__(self):
        return f"{self.user} - {self.program.program_goal}"


# Workout Category Model
class WorkoutCategory(models.Model):
    category_name = models.CharField(max_length=255)
    category_name_uz = models.CharField(max_length=255, blank=True, null=True)
    category_name_ru = models.CharField(max_length=255, blank=True, null=True)
    category_name_en = models.CharField(max_length=255, blank=True, null=True)

    description = models.TextField()
    description_uz = models.TextField(blank=True, null=True)
    description_ru = models.TextField(blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.category_name_uz:
            self.category_name_uz = translate_text(self.category_name, 'uz')
        if not self.category_name_ru:
            self.category_name_ru = translate_text(self.category_name, 'ru')
        if not self.category_name_en:
            self.category_name_en = translate_text(self.category_name, 'en')

        if not self.description_uz:
            self.description_uz = translate_text(self.description, 'uz')
        if not self.description_ru:
            self.description_ru = translate_text(self.description, 'ru')
        if not self.description_en:
            self.description_en = translate_text(self.description, 'en')

        super(WorkoutCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.category_name


# Session Model
class Session(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE,related_name="sessions")
    calories_burned = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    session_number = models.IntegerField(null=False)
    session_time = models.TimeField(null=True, blank=True)
    exercises = models.ManyToManyField('Exercise', related_name='sessions')
    meals = models.ManyToManyField('Meal', related_name='sessions')

    def __str__(self):
        return f"Session on {self.session_number} - {self.program}"


class SessionCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="session_completions")
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="completions")
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)
    session_date = models.DateField(null=True, blank=True)  # New field for planned date
    session_number_private = models.IntegerField(null=False)


    class Meta:
        unique_together = ('user', 'session')  # Ensures unique tracking per user-session combination

    def save(self, *args, **kwargs):
        if self.is_completed and not self.completion_date:
            self.completion_date = timezone.now().date()
        super(SessionCompletion, self).save(*args, **kwargs)

    def __str__(self):
        status = "Completed" if self.is_completed else "Pending"
        return f"{self.user.email_or_phone} - {self.session.program.program_goal} ({status})"


class Exercise(models.Model):
    category = models.ForeignKey(WorkoutCategory, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    name_uz = models.CharField(max_length=255, blank=True, null=True)
    name_ru = models.CharField(max_length=255, blank=True, null=True)
    name_en = models.CharField(max_length=255, blank=True, null=True)

    description = models.TextField()
    description_uz = models.TextField(blank=True, null=True)
    description_ru = models.TextField(blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)

    difficulty_level = models.CharField(max_length=50)  # E.g., Beginner, Intermediate, Advanced
    target_muscle = models.CharField(max_length=255)
    video_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.name_uz:
            self.name_uz = translate_text(self.name, 'uz')
        if not self.name_ru:
            self.name_ru = translate_text(self.name, 'ru')
        if not self.name_en:
            self.name_en = translate_text(self.name, 'en')

        if not self.description_uz:
            self.description_uz = translate_text(self.description, 'uz')
        if not self.description_ru:
            self.description_ru = translate_text(self.description, 'ru')
        if not self.description_en:
            self.description_en = translate_text(self.description, 'en')

        super(Exercise, self).save(*args, **kwargs)

    def __str__(self):
        return self.name






class Meal(models.Model):
    MEAL_TYPES = (
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('snack', 'Snack'),
        ('dinner', 'Dinner'),
    )

    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    food_name = models.CharField(max_length=255)
    food_name_uz = models.CharField(max_length=255, blank=True, null=True)
    food_name_ru = models.CharField(max_length=255, blank=True, null=True)
    food_name_en = models.CharField(max_length=255, blank=True, null=True)
    calories = models.DecimalField(max_digits=5, decimal_places=2, help_text="Calories for this meal")
    water_content = models.DecimalField(max_digits=5, decimal_places=2, help_text="Water content in ml")
    food_photo = models.ImageField(upload_to='meal_photos/', blank=True, null=True)
    preparation_time = models.IntegerField(help_text="Preparation time in minutes")
    meal_type_uz = models.CharField(max_length=20, blank=True, null=True)
    meal_type_ru = models.CharField(max_length=20, blank=True, null=True)
    meal_type_en = models.CharField(max_length=20, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Tarjima qilish
        if not self.food_name_uz:
            self.food_name_uz = translate_text(self.food_name, 'uz')
        if not self.food_name_ru:
            self.food_name_ru = translate_text(self.food_name, 'ru')
        if not self.food_name_en:
            self.food_name_en = translate_text(self.food_name, 'en')

        if not self.meal_type_uz:
            self.meal_type_uz = translate_text(dict(self.MEAL_TYPES).get(self.meal_type), 'uz')
        if not self.meal_type_ru:
            self.meal_type_ru = translate_text(dict(self.MEAL_TYPES).get(self.meal_type), 'ru')
        if not self.meal_type_en:
            self.meal_type_en = translate_text(dict(self.MEAL_TYPES).get(self.meal_type), 'en')

        super(Meal, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.meal_type.capitalize()} for {self.session.user} on {self.session.date}"


class MealCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meal_completions")
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="meal_completions")
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="completions")
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)
    meal_date = models.DateField(null=True, blank=True)  # New field for planned date
    missed = models.BooleanField(default=False) # Track if the meal was missed
    reminder_sent = models.BooleanField(default=False) # Track if a reminder was sent for this meal
    meal_time = models.TimeField(null=True, blank=True) # Time set by user for meal completion



    class Meta:
        unique_together = ('user', 'session', 'meal')  # Ensures unique tracking per user-session-meal combination

    def save(self, *args, **kwargs):
        if self.is_completed and not self.completion_date:
            self.completion_date = timezone.now().date()
        super(MealCompletion, self).save(*args, **kwargs)

    def __str__(self):
        status = "Completed" if self.is_completed else "Pending"
        return f"{self.user.email_or_phone} - {self.meal.food_name} ({status})"


# Preparation model
class Preparation(models.Model):
    meal = models.ForeignKey('Meal', on_delete=models.CASCADE, related_name="preparations")
    name = models.CharField(max_length=255)
    description = models.TextField(help_text="Description of the preparation method")
    preparation_time = models.IntegerField(help_text="Preparation time in minutes")

    # Translated fields
    name_uz = models.CharField(max_length=255, blank=True, null=True)
    name_ru = models.CharField(max_length=255, blank=True, null=True)
    name_en = models.CharField(max_length=255, blank=True, null=True)
    
    description_uz = models.TextField(blank=True, null=True)
    description_ru = models.TextField(blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Check if translations are missing, then add them
        if not self.name_uz:
            self.name_uz = translate_text(self.name, 'uz')
        if not self.name_ru:
            self.name_ru = translate_text(self.name, 'ru')
        if not self.name_en:
            self.name_en = translate_text(self.name, 'en')

        if not self.description_uz:
            self.description_uz = translate_text(self.description, 'uz')
        if not self.description_ru:
            self.description_ru = translate_text(self.description, 'ru')
        if not self.description_en:
            self.description_en = translate_text(self.description, 'en')

        super(Preparation, self).save(*args, **kwargs)

    def __str__(self):
        return f"Preparation for {self.meal.food_name}: {self.name}"



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    message_uz = models.TextField(blank=True, null=True)
    message_ru = models.TextField(blank=True, null=True)
    message_en = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=10, default='en')
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=50, default="general")  # e.g., "reminder", "update"
    scheduled_time = models.TimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.message_uz:
            self.message_uz = translate_text(self.message, 'uz')
        if not self.message_ru:
            self.message_ru = translate_text(self.message, 'ru')
        if not self.message_en:
            self.message_en = translate_text(self.message, 'en')
        super(Notification, self).save(*args, **kwargs)

    def __str__(self):
        return f"Notification for {self.user.email_or_phone} - {self.sent_at}"






