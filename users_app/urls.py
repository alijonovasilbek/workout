from django.urls import path
from users_app.views import OrderCreate
from .views import (
    RegisterView, VerifyCodeView, LoginView, ForgotPasswordView, ResetPasswordView,
    UpdateLanguageView,
    LogoutAPIView,MarkNotificationReadView, UpdateNotificationPreferencesView,
    ProgramLanguageView22,UpdateLanguageView22
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-code/", VerifyCodeView.as_view(), name="verify_code"),
    path("login/", LoginView.as_view(), name="login"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("update-language/", UpdateLanguageView.as_view(), name="update-language"),
    path("notifications/<int:notification_id>/mark-read/", MarkNotificationReadView.as_view(), name="mark_notification_read"),
    path("update-notification-preferences/", UpdateNotificationPreferencesView.as_view(), name="update_notification_preferences"),
    path("logout/",LogoutAPIView.as_view(),name="logout"),
    path("create/", OrderCreate.as_view()),

]



urlpatterns += [
    path('api/programs/language2', ProgramLanguageView22.as_view(), name='programs'),
    path('api/user/language2', UpdateLanguageView22.as_view(), name='update_language'),
]


