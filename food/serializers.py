from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from users_app.models import Preparation, Meal, MealCompletion, Session
from googletrans import Translator

# Initialize the Google Translator
translator = Translator()

def translate_text(text, target_language):
    """Translate the text to the specified language using Google Translate."""
    try:
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        # Log the error and return the original text if translation fails
        print(f"Translation error: {e}")
        return text

class MealSerializer(serializers.ModelSerializer):
    session_date = serializers.DateField(source='session.scheduled_date', read_only=True)
    meal_type = serializers.ChoiceField(choices=Meal.MEAL_TYPES, required=True)
    food_photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Meal
        fields = [
            'id', 'session_date', 'meal_type', 'food_name', 'calories',
            'water_content', 'preparation_time', 'food_photo'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        language = self.context.get("language", "en")  # Get language from context, default to 'en'

        # Translate meal type choices
        meal_type_translations = {
            'breakfast': translate_text('Breakfast', language),
            'lunch': translate_text('Lunch', language),
            'snack': translate_text('Snack', language),
            'dinner': translate_text('Dinner', language)
        }

        # Apply translations for meal type and food name
        data['meal_type'] = meal_type_translations.get(instance.meal_type, instance.meal_type)
        data['food_name'] = translate_text(instance.food_name, language)

        return data

class MealCompletionSerializer(serializers.ModelSerializer):
    meal_name = serializers.CharField(source='meal.food_name', read_only=True)
    meal_calories = serializers.DecimalField(source='meal.calories', max_digits=5, decimal_places=2, read_only=True)
    session_id = serializers.PrimaryKeyRelatedField(queryset=Session.objects.all(), source='session')

    class Meta:
        model = MealCompletion
        fields = ['id', 'meal', 'session_id', 'is_completed', 'completion_date', 'meal_name', 'meal_calories','meal_time']
        read_only_fields = ['completion_date']


    def to_representation(self, instance):
        data = super().to_representation(instance)
        language = self.context.get("language", "en")


        data['meal_name'] = translate_text(instance.meal.food_name, language)

        return data


class PreparationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preparation
        fields = [
            'id', 'meal', 'name', 'description', 'preparation_time'
        ]  # Exclude translated fields from input

        extra_kwargs = {
            'meal': {'label': _("Meal")},
            'name': {'label': _("Name"), 'required': True},
            'description': {'label': _("Description"), 'required': True},
            'preparation_time': {'label': _("Preparation Time"), 'required': True},
        }

    def create(self, validated_data):
        # Automatically translate missing fields if they are not provided
        name = validated_data.get('name', '')
        description = validated_data.get('description', '')

        validated_data['name_uz'] = translate_text(name, 'uz')
        validated_data['name_ru'] = translate_text(name, 'ru')
        validated_data['name_en'] = translate_text(name, 'en')

        validated_data['description_uz'] = translate_text(description, 'uz')
        validated_data['description_ru'] = translate_text(description, 'ru')
        validated_data['description_en'] = translate_text(description, 'en')

        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        language = self.context.get('language', 'en')

        # Return translated fields based on user language
        data['name'] = getattr(instance, f'name_{language}', instance.name)
        data['description'] = getattr(instance, f'description_{language}', instance.description)

        return data


class CompleteMealSerializer(serializers.Serializer):
    session_id = serializers.IntegerField(required=True, help_text="Session ID ni kiriting.")
    meal_id = serializers.IntegerField(required=True, help_text="Meal ID ni kiriting.")

    def validate_meal_completion_id(self, value):
        user = self.context['request'].user
        try:
            meal_completion = MealCompletion.objects.get(id=value, user=user)
        except MealCompletion.DoesNotExist:
            raise serializers.ValidationError("Meal completion not found or you do not have permission to modify it.")
        return value
