import random
import re
import logging
from datetime import datetime, timedelta
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone, translation
from django.contrib.auth import authenticate, login, get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from .serializers import (
    RegisterSerializer, VerifyCodeSerializer, LoginSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer
)
from rest_framework.parsers import JSONParser, FormParser,MultiPartParser
from users_app.models import User, Notification, Program, UserProgram, MealCompletion, Session,SessionCompletion
from users_app.notifications import NotificationService
from .eskiz_api import EskizAPI
from drf_yasg import openapi
from django.db import OperationalError
from django.db import connection

import logging



User = get_user_model()
eskiz_api = EskizAPI()
logger = logging.getLogger(__name__)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class RegisterView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [FormParser, MultiPartParser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('first_name', openapi.IN_FORM, description="First Name", type=openapi.TYPE_STRING),
            openapi.Parameter('last_name', openapi.IN_FORM, description="Last Name", type=openapi.TYPE_STRING),
            openapi.Parameter('email_or_phone', openapi.IN_FORM, description="Email or Phone", type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_FORM, description="Password", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('gender', openapi.IN_FORM, description="Gender", type=openapi.TYPE_STRING, enum=["Male", "Female"]),
            openapi.Parameter('country', openapi.IN_FORM, description="Country", type=openapi.TYPE_STRING, enum=["Uzbekistan", "Russia", "Kazakhstan", "Other"]),
            openapi.Parameter('age', openapi.IN_FORM, description="Age", type=openapi.TYPE_INTEGER),
            openapi.Parameter('height', openapi.IN_FORM, description="Height (in cm)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('weight', openapi.IN_FORM, description="Weight (in kg)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('level', openapi.IN_FORM, description="Level", type=openapi.TYPE_STRING, enum=["Beginner", "Intermediate", "Advanced"]),
            openapi.Parameter(
                'goal',
                openapi.IN_FORM,
                description="Select a Goal",
                type=openapi.TYPE_STRING,
                # Dinamik ravishda enumni yuklashdan oldin tekshirish
                enum=[
                    program.program_goal for program in Program.objects.all()
                ] if Program._meta.db_table in connection.introspection.table_names() else []

            ),
        ],
        responses={200: "Registration successful"}
    )
    def post(self, request):
        # Ensure default goal exists
        try:
            if not Program.objects.exists():
                Program.objects.create(program_goal="General Fitness", goal_type="Default")

            # Dinamik enumlarni yuklashdan oldin tekshirish
            dynamic_goal_enum = Program.objects.values_list('program_goal', flat=True)
        except Exception as e:
            logger.warning(f"Failed to fetch Program model data: {e}")
            dynamic_goal_enum = []

        data = request.data.copy()
        provided_goal = data.get('goal')

        if provided_goal and provided_goal not in dynamic_goal_enum:
            return Response({"error": _("Invalid goal. Please select a valid option.")},
                            status=status.HTTP_400_BAD_REQUEST)

        # Serialize data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            email_or_phone = serializer.validated_data['email_or_phone']
            password = serializer.validated_data['password']

            # Check if user exists
            user = User.objects.filter(email_or_phone=email_or_phone).first()
            if user:
                if user.is_active:
                    return Response({"email_or_phone": _("This email or phone number is already registered.")}, status=status.HTTP_400_BAD_REQUEST)

                # Resend verification code for inactive user
                verification_code = random.randint(1000, 9999)
                try:
                    if "@" in email_or_phone:
                        send_mail(
                            subject=_('Your Verification Code'),
                            message=_('Your verification code is: {code}').format(code=verification_code),
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[email_or_phone],
                        )
                    else:
                        eskiz_api.send_sms(
                            email_or_phone,
                            _("Your verification code is {code}").format(code=verification_code),
                        )
                except Exception as e:
                    logger.error(f"Failed to send verification code: {e}")
                    return Response({"error": _("Failed to send verification code. Please try again.")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                cache.set(f'verification_code_{user.id}', {'code': verification_code, 'timestamp': datetime.now().timestamp()}, timeout=300)
                return Response({"user_id": user.id, "message": _("Verification code resent.")}, status=status.HTTP_200_OK)

            # Create new user
            user = serializer.save(is_active=False)
            user.set_password(password)
            user.save()

            # Send verification code for new user
            verification_code = random.randint(1000, 9999)
            try:
                if "@" in email_or_phone:
                    send_mail(
                        subject=_('Your Verification Code'),
                        message=_('Your verification code is: {code}').format(code=verification_code),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email_or_phone],
                    )
                else:
                    eskiz_api.send_sms(
                        email_or_phone,
                        _("Your verification code is {code}").format(code=verification_code),
                    )
            except Exception as e:
                logger.error(f"Failed to send verification code: {e}")
                return Response({"error": _("Failed to send verification code. Please try again.")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            cache.set(f'verification_code_{user.id}', {'code': verification_code, 'timestamp': datetime.now().timestamp()}, timeout=300)
            return Response({"user_id": user.id, "message": _("User registered successfully.")}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email_or_phone = serializer.validated_data['email_or_phone']
            password = serializer.validated_data['password']

            # Foydalanuvchini topish
            user = User.objects.filter(email_or_phone=email_or_phone).first()
            if user:
                # Agar foydalanuvchi `is_active=False` bo'lsa, uni `True` qilib qo'yamiz
                if not user.is_active:
                    user.is_active = True
                    user.save(update_fields=['is_active'])

                # Parolni tekshirish
                user = authenticate(request, email_or_phone=email_or_phone, password=password)
                if user:
                    # Tizimga kiritish
                    login(request, user)
                    # Token yaratish
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        "message": _("Login successful"),
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }, status=status.HTTP_200_OK)

            # Agar parol noto'g'ri yoki foydalanuvchi mavjud bo'lmasa
            return Response({"error": _("Invalid credentials")}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=VerifyCodeSerializer)
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            entered_code = serializer.validated_data['code']
            user = User.objects.filter(id=user_id).first()

            if user:
                cached_data = cache.get(f'verification_code_{user.id}')
                if cached_data and str(cached_data['code']) == str(entered_code) and \
                        datetime.now() - datetime.fromtimestamp(cached_data['timestamp']) < timedelta(minutes=5):

                    # Activate user and delete the verification code
                    user.is_active = True
                    user.save()
                    cache.delete(f'verification_code_{user.id}')

                    if user.goal:  # Link program based on goal
                        program = Program.objects.filter(program_goal=user.goal).first()
                        if program:
                            # Calculate total sessions
                            total_sessions = program.sessions.count()

                            # Create UserProgram
                            start_date = datetime.now().date()
                            end_date = start_date + timedelta(days=total_sessions)
                            user_program = UserProgram.objects.create(
                                user=user,
                                program=program,
                                start_date=start_date,
                                end_date=end_date
                            )

                            # Assign sessions and meals with predefined dates
                            sessions = Session.objects.filter(program=program).order_by('session_number')
                            for index, session in enumerate(sessions, start=1):
                                # Calculate session date based on session number
                                session_date = start_date + timedelta(days=index - 1)

                                # Create MealCompletion
                                meals = session.meals.all()
                                for meal in meals:
                                    MealCompletion.objects.create(
                                        user=user,
                                        meal=meal,
                                        session=session,
                                        is_completed=False,
                                        meal_date=session_date,  # Assign session_date
                                        completion_date=None,  # Completion date is set upon completion
                                    )

                                # Create SessionCompletion
                                SessionCompletion.objects.create(
                                    user=user,
                                    session=session,
                                    is_completed=False,
                                    session_number_private=session.session_number,
                                    session_date=session_date  # Assign session_date
                                )

                    return Response({"message": _("Verification successful")}, status=status.HTTP_200_OK)

                return Response({"error": _("Verification code expired or invalid")}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": _("User not found")}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=ForgotPasswordSerializer)
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email_or_phone = serializer.validated_data['email_or_phone']
            user = User.objects.filter(email_or_phone=email_or_phone).first()

            if user:
                verification_code = random.randint(1000, 9999)
                cache.set(f'verification_code_{user.id}', verification_code, timeout=300)
                try:
                    if re.match(r'^\+998\d{9}$', email_or_phone):
                        eskiz_api.send_sms(email_or_phone, _("Your password reset verification code is {code}").format(
                            code=verification_code))
                    else:
                        send_mail(
                            subject=_("Your Password Reset Verification Code"),
                            message=_("Your password reset verification code is {code}.").format(
                                code=verification_code),
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email_or_phone]
                        )
                    return Response({"message": _("Verification code sent")}, status=status.HTTP_200_OK)
                except Exception as e:
                    logger.error(f"Failed to send password reset verification: {e}")
                    return Response({"error": _("Failed to send verification code")},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"error": _("User not found")}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email_or_phone = serializer.validated_data['email_or_phone']
            verification_code = serializer.validated_data['verification_code']
            new_password = serializer.validated_data['new_password']
            user = User.objects.filter(email_or_phone=email_or_phone).first()

            if user and str(cache.get(f'verification_code_{user.id}')) == str(verification_code):
                user.set_password(new_password)
                user.save()
                cache.delete(f'verification_code_{user.id}')
                return Response({"message": _("Password reset successful")}, status=status.HTTP_200_OK)

            return Response({"error": _("Invalid or expired verification code")}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)














class UpdateLanguageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        lang_code = request.data.get('language')
        if lang_code in ['en', 'ru', 'uz']:
            request.user.language = lang_code
            request.user.save()
            translation.activate(lang_code)
            request.session['django_language'] = lang_code
            return Response({"message": _("Language updated successfully")}, status=status.HTTP_200_OK)

        return Response({"error": _("Invalid language code")}, status=status.HTTP_400_BAD_REQUEST)


class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        notification = Notification.objects.filter(id=notification_id, user=request.user).first()
        if notification:
            notification.is_read = True
            notification.save()
            return Response({"message": _("Notification marked as read")}, status=status.HTTP_200_OK)

        return Response({"error": _("Notification not found")}, status=status.HTTP_404_NOT_FOUND)


class UpdateNotificationPreferencesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        preferences = request.data.get('notification_preferences')
        if isinstance(preferences, dict):
            request.user.notification_preferences.update(preferences)
            request.user.save()
            return Response({"message": _("Notification preferences updated successfully")}, status=status.HTTP_200_OK)

        return Response({"error": _("Invalid preferences format")}, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Foydalanuvchini is_active ni False qilish
        user.is_active = False
        user.save()

        # Tokenni bekor qilish (agar JWT ishlatilayotgan bo'lsa)
        if hasattr(request.auth, 'delete'):  # Agar token tizimidan foydalansa
            request.auth.delete()

        return Response({"message": _("Foydalanuvchi tizimdan muvaffaqiyatli chiqarildi.")}, status=200)







from rest_framework import views
from rest_framework import response

from payme import Payme

from register import settings
from users_app.serializers import UserPaymentSerializer


payme = Payme(payme_id=settings.PAYME_ID)


class OrderCreate(views.APIView):
    """
    API endpoint for creating an order.
    """
    serializer_class = UserPaymentSerializer

    def post(self, request):
        """
        Create a new order.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        result = {
            "order": serializer.data
        }

        if serializer.data["payment_method"] == "payme":
            payment_link = payme.initializer.generate_pay_link(
                id=serializer.data["id"],
                amount=serializer.data["total_amount"],
                return_url="https://uzum.uz"
            )
            result["payment_link"] = payment_link

        return response.Response(result)


from  users_app.serializers import  ProgramSerializer,LanguageUpdateSerializer


class ProgramLanguageView22(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        language = user.language  # Foydalanuvchi tili

        # Foydalanuvchiga tegishli faol dasturlarni olish
        user_programs = UserProgram.objects.filter(user=user, is_active=True)
        programs = [user_program.program for user_program in user_programs]

        # Tarjima qilingan ma'lumotlarni qaytarish
        serializer = ProgramSerializer(programs, many=True, context={'request': request})

        return Response({
            "message": _("Programs retrieved successfully"),
            "language": language,
            "programs": serializer.data,
        }, status=status.HTTP_200_OK)



from drf_yasg.utils import swagger_auto_schema

class UpdateLanguageView22(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LanguageUpdateSerializer

    @swagger_auto_schema(request_body=LanguageUpdateSerializer)
    def post(self, request):
        serializer = LanguageUpdateSerializer(data=request.data)
        if serializer.is_valid():
            new_language = serializer.validated_data['language']
            user = request.user

            # Foydalanuvchi tilini yangilash
            user.language = new_language
            user.save()

            return Response({"message": _("Language updated successfully")}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)