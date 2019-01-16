from django.contrib import admin
from django.http import HttpResponse

import io
import csv
import zipfile
import time
import datetime

from .models import Vote


# Admin export votes action
def export_votes_as_csv(modeladmin, request, queryset):

    # csv headers's text
    votes_field_names = ["id", "voting_id", "a", "b", "voted"]
    votings_field_names = [
      "id", 
      "name", 
      "desc", 
      "start_date", 
      "end_date", 
      "pub_key_id",
      "postproc", 
      "tally"
      ]

    # current time
    timestamp = time.time()
    current_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d')

    # csv buffers
    votings_file = io.StringIO()
    votes_file = io.StringIO()

    # csv writers
    votings_file_writer = csv.writer(votings_file)
    votes_file_writer = csv.writer(votes_file)

    # writing csv headers
    votings_file_writer.writerow(votings_field_names)
    votes_file_writer.writerow(votes_field_names)

    # iterating votings
    for obj in queryset:
        votes = Vote.objects.filter(voting_id=obj.id)
        votings_file_writer.writerow([getattr(obj, field) for field in votings_field_names])
        # iterating votes by voting
        for v in votes:
            votes_file_writer.writerow([getattr(v, field) for field in votes_field_names])

    # create zip buffer
    zipped_file = io.BytesIO()
    # create zip file 
    zip_file = zipfile.ZipFile(zipped_file, 'w')

    # write csv files
    zip_file.writestr("{}.csv".format("votings_votings_" + current_time), votings_file.getvalue())
    zip_file.writestr("{}.csv".format("votings_votes_" + current_time), votes_file.getvalue())
    
    # close file
    zip_file.close()
    zipped_file.seek(0)    
    
    # creating http response
    response = HttpResponse(zipped_file.read())
    response['Content-Disposition'] = 'attachment; filename={}.zip'.format("votings_"+ current_time)
    response['Content-Type'] = 'application/x-zip'

    return response


# Admin vote model
class VoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'voting_id', 'voter_id', 'voted']
    readonly_fields = ['id', 'voting_id', 'voter_id', 'voted']
    search_fields = ['voting_id', ]


admin.site.register(Vote, VoteAdmin)
