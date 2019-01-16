
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .forms import UserCreateFormAdmin, UserCreationForm, UserChangeForm

from django.contrib.auth import get_user_model 

User=get_user_model()
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreateFormAdmin
    # form = UserCreateForm

    # The fields to be used in displaying the DecideUser model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.DecideDecideDecideDecide.
    SEX_OPTIONS = (
        ('M', 'Man'),
        ('W', 'Woman'),
        ('N', 'Non-binary'),
    )
    list_display = ('email', 'first_name','last_name','city','birthdate', 'sex', 'is_staff')
    list_filter = ('is_staff',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('birthdate','city','sex', 'first_name','last_name'),}),
        ('Permissions', {'fields': ('is_staff',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'birthdate','city','sex', 'first_name','last_name', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
