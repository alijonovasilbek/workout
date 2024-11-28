from datetime import datetime, timedelta

from django.shortcuts import render
from django.utils import timezone
from rest_framework.exceptions import NotAuthenticated
from rest_framework.views import APIView
from django.utils.timezone import now

from users_app.models import Preparation, Meal, MealCompletion, Session
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from food.serializers import MealSerializer, MealCompletionSerializer
from exercise.permissions import IsAdminOrReadOnly
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from googletrans import Translator
from rest_framework.decorators import action

from  food.serializers import  *



translator = Translator()

def translate_text(text, target_language):
    try:
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        # If there's an error, return the original text
        print(f"Translation error: {e}")
        return text


class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # For handling file uploads

    def get_serializer_context(self):
        # Use 'lang' query parameter to determine language, with 'en' as the default
        language = self.request.query_params.get('lang', 'en')
        return {**super().get_serializer_context(), "language": language}

    @swagger_auto_schema(tags=['Meals'], operation_description=_("List all meals for the authenticated user"))
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"meals": serializer.data})

    @swagger_auto_schema(tags=['Meals'], operation_description=_("Retrieve a specific meal"))
    def retrieve(self, request, pk=None):
        meal = self.get_object()
        serializer = self.get_serializer(meal)
        return Response({"meal": serializer.data})

    @swagger_auto_schema(tags=['Meals'], operation_description=_("Create a new meal with optional photo upload"))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Meal created successfully", "meal": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Meals'], operation_description=_("Update a meal by ID"))
    def update(self, request, pk=None, *args, **kwargs):
        meal = self.get_object()
        serializer = self.get_serializer(meal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Meal updated successfully", "meal": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Meals'], operation_description=_("Partially update a meal by ID"))
    def partial_update(self, request, pk=None, *args, **kwargs):
        meal = self.get_object()
        serializer = self.get_serializer(meal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Meal partially updated successfully", "meal": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Meals'], operation_description=_("Delete a meal"))
    def destroy(self, request, pk=None, *args, **kwargs):
        meal = self.get_object()
        meal.delete()
        return Response({"message": "Meal deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class MealCompletionViewSet(viewsets.ModelViewSet):
    queryset = MealCompletion.objects.all()
    serializer_class = MealCompletionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # If the view is accessed by Swagger or the user is not authenticated, return an empty queryset
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return MealCompletion.objects.none()
        return MealCompletion.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        # Use 'lang' query parameter to determine language, with 'en' as the default
        language = self.request.query_params.get('lang', 'en')
        return {**super().get_serializer_context(), "language": language}

    @swagger_auto_schema(tags=['Meal Completions'],
                         operation_description=_("List all meal completions for the authenticated user"))
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"meal_completions": serializer.data})

    @swagger_auto_schema(tags=['Meal Completions'], operation_description=_("Retrieve a specific meal completion"))
    def retrieve(self, request, pk=None):
        meal_completion = self.get_object()
        serializer = self.get_serializer(meal_completion)
        return Response({"meal_completion": serializer.data})

    @swagger_auto_schema(tags=['Meal Completions'], operation_description=_("Create a new meal completion"))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            session = serializer.validated_data.get('session')  # Extract session
            meal = serializer.validated_data.get('meal')  # Extract meal
            user = request.user

            # Ensure the session and meal are valid
            if not Session.objects.filter(id=session.id).exists():
                return Response({"error": _("Invalid session ID.")}, status=status.HTTP_400_BAD_REQUEST)

            if not Meal.objects.filter(id=meal.id).exists():
                return Response({"error": _("Invalid meal ID.")}, status=status.HTTP_400_BAD_REQUEST)

            # Save the meal completion
            meal_completion = serializer.save(user=user)
            return Response(
                {
                    "message": _("Meal completion recorded successfully"),
                    "meal_completion": MealCompletionSerializer(meal_completion).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    @swagger_auto_schema(tags=['Meal Completions'], operation_description=_("Update meal completion status by ID"))
    def update(self, request, pk=None, *args, **kwargs):
        meal_completion = self.get_object()
        serializer = self.get_serializer(meal_completion, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Meal completion updated successfully", "meal_completion": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Meal Completions'], operation_description=_("Partially update a meal completion record"))
    def partial_update(self, request, pk=None, *args, **kwargs):
        meal_completion = self.get_object()
        serializer = self.get_serializer(meal_completion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Meal completion record partially updated successfully", "meal_completion": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def schedule_reminder(self, meal_completion):
        """
        Schedules a reminder for a meal based on the user's preferred reminder time offset.
        """
        user_reminder_offset = getattr(self.request.user, 'reminder_time', None)
        if meal_completion.meal and meal_completion.meal.scheduled_time and user_reminder_offset:
            meal_time = meal_completion.meal.scheduled_time
            reminder_time = datetime.combine(timezone.now().date(), meal_time) - timedelta(
                minutes=user_reminder_offset.minute)

            # Placeholder for scheduling logic
            # Implement your logic to actually schedule the reminder (e.g., using Celery or Django signals)
            print(f"Reminder scheduled at {reminder_time} for meal at {meal_time}")

    @swagger_auto_schema(tags=['Meal Completions'], operation_description=_("Delete a meal completion record"))
    def destroy(self, request, pk=None, *args, **kwargs):
        meal_completion = self.get_object()
        meal_completion.delete()
        return Response({"message": "Meal completion record deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



class PreparationViewSet(viewsets.ModelViewSet):
    queryset = Preparation.objects.all()
    serializer_class = PreparationSerializer
    permission_classes = [IsAuthenticated,IsAdminOrReadOnly]

    def get_queryset(self):
        # Optionally filter based on query parameters
        meal_id = self.request.query_params.get('meal_id')
        if meal_id:
            return self.queryset.filter(meal_id=meal_id)
        return self.queryset

    def get_serializer_context(self):
        # Pass the user's preferred language to the serializer
        context = super().get_serializer_context()
        context['language'] = getattr(self.request.user, 'language', 'en')
        return context

    @action(detail=False, methods=['get'], url_path='by-meal')
    def get_by_meal(self, request):
        meal_id = request.query_params.get('meal_id')
        if not meal_id:
            return Response(
                {"error": _("meal_id is required.")},
                status=status.HTTP_400_BAD_REQUEST
            )

        preparations = self.queryset.filter(meal_id=meal_id)
        serializer = self.get_serializer(preparations, many=True)
        return Response({"preparations": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='translate')
    def translate_fields(self, request, pk=None):
        preparation = self.get_object()

        # Translate fields if they are missing
        if not preparation.name_uz:
            preparation.name_uz = translate_text(preparation.name, 'uz')
        if not preparation.name_ru:
            preparation.name_ru = translate_text(preparation.name, 'ru')
        if not preparation.name_en:
            preparation.name_en = translate_text(preparation.name, 'en')

        if not preparation.description_uz:
            preparation.description_uz = translate_text(preparation.description, 'uz')
        if not preparation.description_ru:
            preparation.description_ru = translate_text(preparation.description, 'ru')
        if not preparation.description_en:
            preparation.description_en = translate_text(preparation.description, 'en')

        preparation.save()
        return Response({"message": _("Fields translated successfully.")}, status=status.HTTP_200_OK)


from drf_yasg import openapi


class CompleteMealView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=CompleteMealSerializer,
        responses={
            200: "Taom muvaffaqiyatli bajarildi.",
            404: "Session va Meal kombinatsiyasi topilmadi."
        }
    )
    def post(self, request):
        serializer = CompleteMealSerializer(data=request.data)
        if serializer.is_valid():
            session_id = serializer.validated_data.get('session_id')
            meal_id = serializer.validated_data.get('meal_id')

            # MealCompletion obyektini topish
            meal_completion = MealCompletion.objects.filter(
                session_id=session_id,
                meal_id=meal_id,
                user=request.user
            ).first()

            if not meal_completion:
                return Response({"error": "Session va Meal kombinatsiyasi topilmadi."}, status=404)

            if meal_completion.is_completed:
                return Response({"message": "Ushbu taom allaqachon bajarilgan."}, status=200)

            # MealCompletionni bajarilgan deb belgilash
            meal_completion.is_completed = True
            meal_completion.completion_date = now().date()
            meal_completion.save()

            return Response({"message": "Taom muvaffaqiyatli bajarildi."}, status=200)

        return Response(serializer.errors, status=400)