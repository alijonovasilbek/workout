from rest_framework import viewsets, permissions
from rest_framework.response import Response
from users_app.models import Program, Session, Exercise, WorkoutCategory, Food, Preparation, Meal, MealFood
from exercise.serializers import ProgramSerializer, SessionSerializer, ExerciseSerializer, WorkoutCategorySerializer, FoodSerializer, PreparationSerializer, MealSerializer, MealFoodSerializer
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from exercise.permissions import IsAdminOrReadOnly
from datetime import timedelta

# Program ViewSet
class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Program.objects.all()
        return Program.objects.filter(is_active=True, purchased_users=self.request.user)

    @swagger_auto_schema(tags=['Programs'], operation_description="List all active programs")
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"programs": serializer.data})

    @swagger_auto_schema(tags=['Programs'], operation_description="Retrieve program by ID")
    def retrieve(self, request, pk=None):
        program = self.get_object()
        serializer = self.get_serializer(program)
        return Response({"program": serializer.data})

    @swagger_auto_schema(tags=['Programs'], operation_description="Create a new program")
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not request.user.is_superuser:
                return Response({"error": _("You do not have permission to create a program.")}, status=403)
            program = serializer.save()
            self._auto_schedule_sessions(program)
            return Response({"message": _("Program created successfully"), "program": serializer.data})
        return Response(serializer.errors, status=400)

    def _auto_schedule_sessions(self, program):
        """Automatically schedule sessions based on frequency_per_week."""
        start_date = program.start_date
        for i in range(program.total_sessions):
            session_date = start_date + timedelta(days=(i // program.frequency_per_week) * 7 + (i % program.frequency_per_week))
            Session.objects.create(program=program, scheduled_date=session_date)

    @swagger_auto_schema(tags=['Programs'], operation_description="Update a program by ID")
    def update(self, request, pk=None):
        program = self.get_object()
        serializer = self.get_serializer(program, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": _("Program updated successfully"), "program": serializer.data})
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(tags=['Programs'], operation_description="Partially update a program by ID")
    def partial_update(self, request, pk=None):
        program = self.get_object()
        serializer = self.get_serializer(program, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": _("Program partially updated successfully"), "program": serializer.data})
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(tags=['Programs'], operation_description="Delete a program")
    def destroy(self, request, pk=None):
        if not request.user.is_superuser:
            return Response({"error": _("You do not have permission to delete a program.")}, status=403)
        program = self.get_object()
        program.delete()
        return Response({"message": _("Program deleted successfully")})

# Session ViewSet
class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(tags=['Sessions'], operation_description="List all sessions for a specific program")
    def list(self, request):
        program_id = request.query_params.get('program_id')
        queryset = self.get_queryset().filter(program_id=program_id) if program_id else self.get_queryset()
        if not request.user.is_superuser:
            queryset = queryset.filter(program__is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"sessions": serializer.data})

    @swagger_auto_schema(tags=['Sessions'], operation_description="Retrieve session by ID")
    def retrieve(self, request, pk=None):
        session = self.get_object()
        serializer = self.get_serializer(session)
        return Response({"session": serializer.data})

    @swagger_auto_schema(tags=['Sessions'], operation_description="Create a new session for a program")
    def create(self, request):
        if not request.user.is_superuser:
            return Response({"error": _("You do not have permission to create a session.")}, status=403)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": _("Session created successfully"), "session": serializer.data})
        return Response(serializer.errors, status=400)

    def perform_update(self, serializer):
        session = serializer.save()
        if session.completion_status and session.program.progress < session.program.total_sessions:
            session.program.progress += 1
            session.program.save()
            if session.program.progress >= session.program.total_sessions:
                session.program.is_active = False
                session.program.save()

    @swagger_auto_schema(tags=['Sessions'], operation_description="Update a session by ID")
    def update(self, request, pk=None):
        session = self.get_object()
        if not request.user.is_superuser:
            return Response({"error": _("You do not have permission to update this session.")}, status=403)
        serializer = self.get_serializer(session, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": _("Session updated successfully"), "session": serializer.data})
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(tags=['Sessions'], operation_description="Partially update a session by ID")
    def partial_update(self, request, pk=None):
        session = self.get_object()
        if not request.user.is_superuser:
            return Response({"error": _("You do not have permission to partially update this session.")}, status=403)
        serializer = self.get_serializer(session, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": _("Session partially updated successfully"), "session": serializer.data})
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(tags=['Sessions'], operation_description="Delete a session")
    def destroy(self, request, pk=None):
        if not request.user.is_superuser:
            return Response({"error": _("You do not have permission to delete this session.")}, status=403)
        session = self.get_object()
        session.delete()
        return Response({"message": _("Session deleted successfully")})

# Exercise ViewSet
class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(tags=['Exercises'], operation_description="List exercises for a specific session")
    def list(self, request):
        session_id = request.query_params.get('session_id')
        queryset = self.get_queryset().filter(session_id=session_id) if session_id else self.get_queryset()
        if not request.user.is_superuser:
            queryset = queryset.filter(session__program__is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"exercises": serializer.data})

    @swagger_auto_schema(tags=['Exercises'], operation_description="Retrieve exercise by ID")
    def retrieve(self, request, pk=None):
        exercise = self.get_object()
        serializer = self.get_serializer(exercise)
        return Response({"exercise": serializer.data})

    @swagger_auto_schema(tags=['Exercises'], operation_description="Create a new exercise")
    def create(self, request):
        if not request.user.is_superuser:
            return Response({"error": _("You do not have permission to create an exercise.")}, status=403)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": _("Exercise created successfully"), "exercise": serializer.data})
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(tags=['Exercises'], operation_description="Update an exercise by ID")
    def update(self, request, pk=None):
        exercise = self.get_object()
        if not request.user.is_superuser:
            return Response({"error": _("You do not have permission to update this exercise.")}, status=403)
        serializer = self.get_serializer(exercise, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": _("Exercise updated successfully"), "exercise": serializer.data})
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(tags=['Exercises'], operation_description="Partially update an exercise by ID")
    def partial_update(self, request, pk=None):
        exercise = self.get_object()
        if not request.user.is_superuser:
            return Response({"error": _("You do not have permission to partially update this exercise.")}, status=403)
        serializer = self.get_serializer(exercise, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": _("Exercise partially updated successfully"), "exercise": serializer.data})
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(tags=['Exercises'], operation_description="Delete an exercise")
    def destroy(self, request, pk=None):
        if not request.user.is_superuser:
            return Response({"error": _("You do not have permission to delete this exercise.")}, status=403)
        exercise = self.get_object()
        exercise.delete()
        return Response({"message": _("Exercise deleted successfully")})

# Workout Category ViewSet
class WorkoutCategoryViewSet(viewsets.ModelViewSet):
    queryset = WorkoutCategory.objects.all()
    serializer_class = WorkoutCategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(tags=['Workout Categories'], operation_description="List all workout categories")
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"workout_categories": serializer.data})

    @swagger_auto_schema(tags=['Workout Categories'], operation_description="Retrieve workout category by ID")
    def retrieve(self, request, pk=None):
        workout_category = self.get_object()
        serializer = self.get_serializer(workout_category)
        return Response({"workout_category": serializer.data})

    @swagger_auto_schema(tags=['Workout Categories'], operation_description="Create a new workout category")
    def create(self, request):
        if not request.user.is_superuser:
            return Response({"error": _("You do not have permission to create a workout category.")}, status=403)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": _("Workout category created successfully"), "workout_category": serializer.data})
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(tags=['Workout Categories'], operation_description="Update a workout category by ID")
    def update(self, request, pk=None):
        workout_category = self.get_object()
        if not request.user.is_superuser:
            return Response({"error": _("You do not have permission to update this workout category.")}, status=403)
        serializer = self.get_serializer(workout_category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": _("Workout category updated successfully"), "workout_category": serializer.data})
        return Response(serializer.errors, status=400)


    @swagger_auto_schema(tags=['Workout Categories'], operation_description="Partially update a workout category by ID")
    def partial_update(self, request, pk=None):
        workout_category = self.get_object()
        # Only allow superuser to partially update
        if not request.user.is_superuser:
            return Response({"error": _("You do not have permission to partially update this workout category.")},
                            status=403)

        serializer = self.get_serializer(workout_category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": _("Workout category updated successfully"), "workout_category": serializer.data})
        return Response(serializer.errors, status=400)



    @swagger_auto_schema(tags=['Workout Categories'], operation_description="Delete a workout category")
    def destroy(self, request, pk=None):
        if not request.user.is_superuser:
            return Response({"error": _("You do not have permission to delete this workout category.")}, status=403)
        workout_category = self.get_object()
        workout_category.delete()
        return Response({"message": _("Workout category deleted successfully")})
