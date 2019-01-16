from django import forms
from django.contrib.auth import get_user_model 
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
import datetime
import pytz
from django.utils import timezone
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from nocaptcha_recaptcha.fields import NoReCaptchaField

User=get_user_model()
class UserCreateForm(UserCreationForm):
    SEX_OPTIONS = (
        ('M', _('Man')),
        ('W', _('Woman')),
        ('N', _('Non-binary')),
    )
    aux=_("Format: dd/mm/YYYY"),

    first_name = forms.CharField(label=_('First name'),required=False)
    last_name = forms.CharField(label=_('Last name'),required=False)
    email = forms.EmailField(label=_('Email'),required=True)
    birthdate = forms.DateTimeField(label=_('Birthdate'),input_formats=['%d/%m/%Y'], help_text=aux, required=False)
    city = forms.CharField(label=_('City'),required=True)
    sex = forms.ChoiceField(label=_('Sex'),choices=SEX_OPTIONS, required=False)
    captcha = NoReCaptchaField()

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "birthdate", "city", "sex", "password1", "password2", "captcha")
    
    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.birthdate = self.cleaned_data["birthdate"]
        user.city = self.cleaned_data["city"]
        user.sex = self.cleaned_data["sex"]

        if commit:
            user.save()
        return user

    #  Validations  

    def clean(self, *args, **kwargs):
        cleaned_data = super(UserCreateForm, self).clean(*args, **kwargs)
        email = cleaned_data.get('email', None)
        if email is not None:# look for in db
            users = User.objects.all()

            for u in users:
                if email==u.email:
                    self.add_error('email', _('Email alredy exits'))
                    break
                    
        birthdate= cleaned_data.get('birthdate', None)
        if birthdate is not None:
            now = timezone.now()
            
            if birthdate > now:
                self.add_error('birthdate', _('Future date not posible'))

class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'birthdate', 'is_active')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        return self.initial["password"]


# Formulario sin el campo "captcha" necesario para crear el User desde el panel de administracion
class UserCreateFormAdmin(UserCreationForm):
    SEX_OPTIONS = (
        ('M', _('Man')),
        ('W', _('Woman')),
        ('N', _('Non-binary')),
    )
    aux=_("Format: dd/mm/YYYY"),

    first_name = forms.CharField(label=_('First name'),required=False)
    last_name = forms.CharField(label=_('Last name'),required=False)
    email = forms.EmailField(label=_('Email'),required=True)
    birthdate = forms.DateTimeField(label=_('Birthdate'),input_formats=['%d/%m/%Y'], help_text=aux, required=False)
    city = forms.CharField(label=_('City'),required=True)
    sex = forms.ChoiceField(label=_('Sex'),choices=SEX_OPTIONS, required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "birthdate", "city", "sex", "password1", "password2")
    
    def save(self, commit=True):
        user = super(UserCreateFormAdmin, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.birthdate = self.cleaned_data["birthdate"]
        user.city = self.cleaned_data["city"]
        user.sex = self.cleaned_data["sex"]

        if commit:
            user.save()
        return user

    #  Validations  
    
    def clean(self, *args, **kwargs):
        cleaned_data = super(UserCreateFormAdmin, self).clean(*args, **kwargs)
        email = cleaned_data.get('email', None)
        if email is not None:# look for in db
            users = User.objects.all()

            for u in users:
                if email==u.email:
                    self.add_error('email', _('Email alredy exits'))
                    break
                    
        birthdate= cleaned_data.get('birthdate', None)
        if birthdate is not None:
            now = timezone.now() 
            
            if birthdate > now:
                self.add_error('birthdate', _('Future date not posible'))
