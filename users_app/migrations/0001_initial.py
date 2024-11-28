# Generated by Django 5.1.2 on 2024-11-23 15:05

import django.core.validators
import django.db.models.deletion
import users_app.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Exercise",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("name_uz", models.CharField(blank=True, max_length=255, null=True)),
                ("name_ru", models.CharField(blank=True, max_length=255, null=True)),
                ("name_en", models.CharField(blank=True, max_length=255, null=True)),
                ("description", models.TextField()),
                ("description_uz", models.TextField(blank=True, null=True)),
                ("description_ru", models.TextField(blank=True, null=True)),
                ("description_en", models.TextField(blank=True, null=True)),
                ("difficulty_level", models.CharField(max_length=50)),
                ("target_muscle", models.CharField(max_length=255)),
                ("video_url", models.URLField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Meal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "meal_type",
                    models.CharField(
                        choices=[
                            ("breakfast", "Breakfast"),
                            ("lunch", "Lunch"),
                            ("snack", "Snack"),
                            ("dinner", "Dinner"),
                        ],
                        max_length=20,
                    ),
                ),
                ("food_name", models.CharField(max_length=255)),
                (
                    "food_name_uz",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "food_name_ru",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "food_name_en",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "calories",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Calories for this meal",
                        max_digits=5,
                    ),
                ),
                (
                    "water_content",
                    models.DecimalField(
                        decimal_places=2, help_text="Water content in ml", max_digits=5
                    ),
                ),
                (
                    "food_photo",
                    models.ImageField(blank=True, null=True, upload_to="meal_photos/"),
                ),
                (
                    "preparation_time",
                    models.IntegerField(help_text="Preparation time in minutes"),
                ),
                (
                    "meal_type_uz",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                (
                    "meal_type_ru",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                (
                    "meal_type_en",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Program",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "frequency_per_week",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(7),
                        ]
                    ),
                ),
                ("total_sessions", models.IntegerField(default=0)),
                ("progress", models.IntegerField(default=0)),
                ("program_goal", models.CharField(max_length=255)),
                (
                    "program_goal_uz",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "program_goal_ru",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "program_goal_en",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("goal_type", models.CharField(max_length=255)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="WorkoutCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("category_name", models.CharField(max_length=255)),
                (
                    "category_name_uz",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "category_name_ru",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "category_name_en",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("description", models.TextField()),
                ("description_uz", models.TextField(blank=True, null=True)),
                ("description_ru", models.TextField(blank=True, null=True)),
                ("description_en", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("first_name", models.CharField(max_length=30)),
                ("last_name", models.CharField(max_length=30)),
                ("email_or_phone", models.CharField(max_length=255, unique=True)),
                ("password", models.CharField(max_length=128)),
                (
                    "gender",
                    models.CharField(
                        choices=[("Male", "Male"), ("Female", "Female")], max_length=10
                    ),
                ),
                (
                    "country",
                    models.CharField(
                        choices=[
                            ("Uzbekistan", "Uzbekistan"),
                            ("Russia", "Russia"),
                            ("Kazakhstan", "Kazakhstan"),
                            ("Other", "Other"),
                        ],
                        default="Other",
                        max_length=50,
                    ),
                ),
                (
                    "notification_preferences",
                    models.JSONField(
                        default=users_app.models.default_notification_preferences
                    ),
                ),
                ("reminder_time", models.TimeField(blank=True, null=True)),
                (
                    "age",
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(16),
                            django.core.validators.MaxValueValidator(50),
                        ]
                    ),
                ),
                (
                    "height",
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(140),
                            django.core.validators.MaxValueValidator(220),
                        ]
                    ),
                ),
                (
                    "weight",
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(30),
                            django.core.validators.MaxValueValidator(200),
                        ]
                    ),
                ),
                ("goal", models.CharField(max_length=255)),
                ("level", models.CharField(max_length=50)),
                ("is_premium", models.BooleanField(default=False)),
                ("photo", models.ImageField(upload_to="user_photos/")),
                (
                    "language",
                    models.CharField(
                        choices=[("en", "English"), ("ru", "Russian"), ("uz", "Uzbek")],
                        default="en",
                        max_length=5,
                    ),
                ),
                ("is_active", models.BooleanField(default=False)),
                ("is_staff", models.BooleanField(default=False)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True, related_name="custom_user_groups", to="auth.group"
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        related_name="custom_user_permissions",
                        to="auth.permission",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message", models.TextField()),
                ("message_uz", models.TextField(blank=True, null=True)),
                ("message_ru", models.TextField(blank=True, null=True)),
                ("message_en", models.TextField(blank=True, null=True)),
                ("language", models.CharField(default="en", max_length=10)),
                ("sent_at", models.DateTimeField(auto_now_add=True)),
                ("is_read", models.BooleanField(default=False)),
                (
                    "notification_type",
                    models.CharField(default="general", max_length=50),
                ),
                ("scheduled_time", models.TimeField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Preparation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "description",
                    models.TextField(help_text="Description of the preparation method"),
                ),
                (
                    "preparation_time",
                    models.IntegerField(help_text="Preparation time in minutes"),
                ),
                ("name_uz", models.CharField(blank=True, max_length=255, null=True)),
                ("name_ru", models.CharField(blank=True, max_length=255, null=True)),
                ("name_en", models.CharField(blank=True, max_length=255, null=True)),
                ("description_uz", models.TextField(blank=True, null=True)),
                ("description_ru", models.TextField(blank=True, null=True)),
                ("description_en", models.TextField(blank=True, null=True)),
                (
                    "meal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="preparations",
                        to="users_app.meal",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Session",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "calories_burned",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
                ),
                ("session_number", models.IntegerField()),
                ("session_time", models.TimeField(blank=True, null=True)),
                (
                    "exercises",
                    models.ManyToManyField(
                        related_name="sessions", to="users_app.exercise"
                    ),
                ),
                (
                    "meals",
                    models.ManyToManyField(
                        related_name="sessions", to="users_app.meal"
                    ),
                ),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sessions",
                        to="users_app.program",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserProgram",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("progress", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_programs",
                        to="users_app.program",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_programs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserProgress",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("completed_sessions", models.IntegerField(default=0)),
                (
                    "total_calories_burned",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
                ),
                (
                    "calories_gained",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
                ),
                ("missed_sessions", models.IntegerField(default=0)),
                ("week_number", models.IntegerField()),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="users_app.program",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="exercise",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="users_app.workoutcategory",
            ),
        ),
        migrations.CreateModel(
            name="MealCompletion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_completed", models.BooleanField(default=False)),
                ("completion_date", models.DateField(blank=True, null=True)),
                ("meal_date", models.DateField(blank=True, null=True)),
                ("missed", models.BooleanField(default=False)),
                ("reminder_sent", models.BooleanField(default=False)),
                ("meal_time", models.TimeField(blank=True, null=True)),
                (
                    "meal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="completions",
                        to="users_app.meal",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="meal_completions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="meal_completions",
                        to="users_app.session",
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "session", "meal")},
            },
        ),
        migrations.CreateModel(
            name="SessionCompletion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_completed", models.BooleanField(default=False)),
                ("completion_date", models.DateField(blank=True, null=True)),
                ("session_date", models.DateField(blank=True, null=True)),
                ("session_number_private", models.IntegerField()),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="completions",
                        to="users_app.session",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="session_completions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "session")},
            },
        ),
    ]
