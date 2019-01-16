from django import forms
from django.forms import ModelMultipleChoiceField
from authentication.models import User
from voting.models import Voting
from django.db.models import Q
from django.forms.widgets import MultiWidget

# Contiene todos los formularios de la aplicación Census

# Constantes

MAN = 'M'
WOMEN = 'W'
NON_BINARY = 'N'

DATE_INPUT_FORMATS = ['%d/%m/%Y']

# Campos personalizados


class ModelMultipleChoiceFieldByCity(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.__getattribute__('city')


class CensusAddMultipleVotersForm(forms.Form):
    # Preparando valores de los atributos

    SEX_OPTIONS = (
        (MAN, 'Man'),
        (WOMEN, 'Woman'),

        (NON_BINARY, 'Non-binary'),
    )

    # Atributos del formulario

    voting = forms.ModelChoiceField(label='Seleccione una votación', empty_label="-",
                                    queryset=Voting.objects.all().filter(start_date__isnull=True,
                                                                         end_date__isnull=True), required=True,)

    sex = forms.MultipleChoiceField(label='Sex', choices=SEX_OPTIONS, required=False)

    city = forms.CharField(label='City', widget=forms.TextInput(attrs={'placeholder': 'Ej: Sevilla'}), required=False)

    # city = ModelMultipleChoiceFieldByCity(label='City',
    #                                      queryset=User.objects.all().distinct().filter(~Q(city='')).order_by('city'),
    #                                      required=False)

    age_initial_range = forms.DateField(label='Edad inicial',
                                        widget=forms.TextInput(attrs={'placeholder': 'Ej: 22/12/1990'}),
                                        input_formats=DATE_INPUT_FORMATS, required=False)

    age_final_range = forms.DateField(label='Edad final',
                                      widget=forms.TextInput(attrs={'placeholder': 'Ej: 21/10/2008'}),
                                      required=False)
