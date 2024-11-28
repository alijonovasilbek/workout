from django.contrib import admin


from users_app.models import UserProgram


class UserProgramAdmin(admin.ModelAdmin):
    """
    Custom admin interface for PaymeTransactions model.
    """
    list_display = ('id', 'user_id', 'program_id', 'total_amount', 'is_paid', 'payment_method')
    list_filter = ('is_paid', 'payment_method')
    search_fields = ('id', 'user_id', 'total_amount', 'payment_method')



admin.site.register(UserProgram, UserProgramAdmin)
