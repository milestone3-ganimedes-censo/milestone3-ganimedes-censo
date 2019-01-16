from django.contrib import admin
from django.utils import timezone
from django.http import HttpResponse

import csv
import time
import datetime

from .models import QuestionOption
from .models import Question
from .models import Voting

from .filters import StartedFilter

from store.admin import export_votes_as_csv


def start(modeladmin, request, queryset):
    for v in queryset.all():
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()


def stop(ModelAdmin, request, queryset):
    for v in queryset.all():
        v.end_date = timezone.now()
        v.save()


def tally(ModelAdmin, request, queryset):
    for v in queryset.filter(end_date__lt=timezone.now()):
        token = request.session.get('auth-token', '')
        v.tally_votes(token)

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption

class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]
    


class VotingAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    readonly_fields = ('start_date', 'end_date', 'pub_key',
                       'tally', 'postproc')
    date_hierarchy = 'start_date'
    list_filter = (StartedFilter,)
    search_fields = ('name', )

    actions = [ start, stop, tally, export_votes_as_csv ]


admin.site.register(Voting, VotingAdmin)
admin.site.register(Question, QuestionAdmin)
