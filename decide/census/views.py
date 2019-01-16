from django.contrib import messages
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from rest_framework import generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.status import (
        HTTP_201_CREATED as ST_201,
        HTTP_204_NO_CONTENT as ST_204,
        HTTP_400_BAD_REQUEST as ST_400,
        HTTP_401_UNAUTHORIZED as ST_401,
        HTTP_409_CONFLICT as ST_409
)

from base.perms import CensusPermissions
from census import models
from census.forms import CensusAddMultipleVotersForm
from .models import Census
from voting.models import Voting
from authentication.models import User
from census.serializer import CensusSerializer

from authentication import *
from django.views.generic import TemplateView

from django.http import HttpResponse
from django.template import loader
import csv, io
from datetime import datetime
from census.utils import check_str_is_int, check_voting_is_started, internacionalize_message


def addAllRegistered(request):

    voters = User.objects.all()
    voting_id = request.GET.get('voting_id')
    list_voting = list(Voting.objects.all().values_list('id', flat=True))
    if request.user.is_staff:
        if int(voting_id) in list_voting:
            if not check_voting_is_started(int(voting_id)):
                for voter in voters:
                    try:
                        census = Census(voting_id=voting_id, voter_id=voter.id)
                        census.save()
                    except IntegrityError:
                        continue
                        
            else:
                messages.add_message(request, messages.ERROR, internacionalize_message("The voting is started"))
        else:
            messages.add_message(request, messages.ERROR, internacionalize_message("Invalid voting id"))
    else:
        messages.add_message(request, messages.ERROR, internacionalize_message("Permission denied"))

    return redirect('listCensus')


def addAllBySex(request):

    voting_id = request.GET.get('voting_id')
    sex = request.GET.get('sex')
    voters = User.objects.filter(sex=sex)

    list_voting = set(Voting.objects.all().values_list('id', flat=True))

    if request.user.is_staff:
        if voters:
            if int(voting_id) in list_voting:
                if not check_voting_is_started(int(voting_id)):
                    for voter in voters:
                        try:
                            census = Census(voting_id=voting_id, voter_id=voter.id)
                            census.save()
                        except IntegrityError:
                            continue

                else:
                    messages.add_message(request, messages.ERROR, internacionalize_message("The voting is started"))
            else:
                messages.add_message(request, messages.ERROR, internacionalize_message("Invalid voting id"))
        else:
                messages.add_message(request, messages.WARNING, internacionalize_message("No users with sex requested"))
    else:
        messages.add_message(request, messages.ERROR, internacionalize_message("Permission denied"))

    #return redirect('/census/?voting_id=' + voting_id)
    return redirect('listCensus')


def addAllInCity(request):

    voting_id = request.GET.get('voting_id')
    city = request.GET.get('city')
    voters = User.objects.filter(city__iexact=city)

    list_voting = set(Voting.objects.all().values_list('id', flat=True))

    if request.user.is_staff:
        if voters:
            if int(voting_id) in list_voting:
                if not check_voting_is_started(int(voting_id)):
                    for voter in voters:
                        try:
                            census = Census(voting_id=voting_id, voter_id=voter.id)
                            census.save()
                        except IntegrityError:
                            continue
                else:
                    messages.add_message(request, messages.ERROR, internacionalize_message("The voting is started"))
            else:
                messages.add_message(request, messages.ERROR, internacionalize_message("Invalid voting id"))
        else:
                messages.add_message(request, messages.WARNING, internacionalize_message("No users in city requested"))
    else:
        messages.add_message(request, messages.ERROR, internacionalize_message("Permission denied"))

    #return redirect('/census/?voting_id=' + voting_id)
    return redirect('listCensus')


def addAllByAge(request):

    if request.user.is_staff:
        voting_id = request.GET.get('voting_id')

        list_voting = set(Voting.objects.all().values_list('id', flat=True))

        if int(voting_id) in list_voting:
            if not check_voting_is_started(int(voting_id)):
                younger = request.GET.get('younger')
                older = request.GET.get('older')

                if older is None or len(older) == 0: #Comprobando que la edad no este vacía.
                    older = '200'

                if younger is None or len(younger) == 0:
                    younger = '-1'

                if check_str_is_int(older) and check_str_is_int(younger): #Comprobando que en caso de tener un valor sea un entero.

                    now1 = datetime.now()
                    now2 = now1
                    superior_limit = now1.replace(year=now1.year-int(younger))
                    lower_limit = now2.replace(year=now2.year-int(older))

                    voters = User.objects.filter(birthdate__gte=lower_limit)
                    voters = voters.filter(birthdate__lte=superior_limit)

                    if voters:
                        for voter in voters:

                            try:
                                census = Census(voting_id=int(voting_id), voter_id=voter.id)
                                census.save()

                            except IntegrityError:
                                continue

                else:
                    messages.add_message(request, messages.ERROR, internacionalize_message("Age is not an integer"))

            else:
                messages.add_message(request, messages.ERROR, internacionalize_message("The voting is started"))

        else:
            messages.add_message(request, messages.ERROR, internacionalize_message("Invalid voting id"))

    else:
        messages.add_message(request, messages.ERROR, internacionalize_message("Permission denied"))

    return redirect('listCensus')

class CensusCreate(generics.ListCreateAPIView):
    permission_classes = (CensusPermissions,)
    serializer_class = CensusSerializer

    def create(self, request, *args, **kwargs):

        voting_id = request.data.get('voting_id')
        voters = request.data.get('voters')

        users = User.objects.all().values_list('id', flat=True)

        try:
            for voter in voters:
                if int(voter) not in users:
                    return Response('Voter id does not exist', status=ST_409)

                else:
                    census = Census(voting_id=voting_id, voter_id=voter)
                    census.save()

        except IntegrityError:
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        return Response({'voters': voters})


class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        census = Census.objects.filter(voting_id=voting_id, voter_id__in=voters)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response('Valid voter')


# Formularios

def add_custom_census(request):

    if request.user.is_staff:

        if request.method == 'POST':                                    # Petición POST

            form = CensusAddMultipleVotersForm(request.POST)

            # Paso 1: Comprobando que los datos se han añadido al formulario correctamente

            if form.is_valid():
                sex_elections = form.cleaned_data['sex']
                city_election = form.cleaned_data['city']
                age_initial_range_election = form.cleaned_data['age_initial_range']
                age_final_range_election = form.cleaned_data['age_final_range']
                voting = form.cleaned_data['voting'].__getattribute__('pk')

                # Paso 2: Filtrando los votantes seleccionados...

                voters = User.objects.all()

                # ...por sexos

                if len(sex_elections) != 0:                                 # Si la lista tiene 0 elementos...
                    voters = voters.filter(sex__in=sex_elections)

                # ...por ciudades

                if len(city_election) != 0:                                 # Si la longitud de la cadena es 0...
                    voters = voters.filter(city__iexact=city_election)      # Sin considerar mayúsculas y minúsculas

                # ...por rango de edades

                if age_initial_range_election is not None:                  # Si no se especificó fecha de inicio...
                    voters = voters.filter(birthdate__gte=age_initial_range_election)

                if age_final_range_election is not None:                    # Si no se especificó fecha de fin...
                    voters = voters.filter(birthdate__lte=age_final_range_election)

                # Paso 3: comprobamos que el usuario logueado tiene permisos de creación de censos

                if request.user.is_authenticated:

                    # Paso 4: asignamos todos los votantes al nuevo censo

                    voters_ids = voters.values_list('id', flat=True, named=False)



                    for voter_id in voters_ids:

                        # Comprobamos que sea único

                        if not is_exists_census(voting, voter_id):

                            census = Census(voting_id=voting, voter_id=voter_id)
                            census.save()

                return redirect('listCensus')

        else:                                                            # Petición GET
            form = CensusAddMultipleVotersForm()

        context = {
            'form': form,
        }

        return render(request, template_name='add_custom_census.html', context=context)

    else:
        messages.add_message(request, messages.ERROR, internacionalize_message("Permission denied"))

        return redirect('listCensus')

def export_csv(request):

    # Paso 1: creamos un HTTPResponse con el apropiado CSV Header

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="census.csv"'

    # Paso 2: capturamos todos los datos

    census = Census.objects.all()
    cabecera = [field.attname for field in Census._meta.get_fields()]

    # Paso 3: escribimos el fichero CSV

    writer = csv.writer(response)
    writer.writerow(cabecera)

    for row in census:
        writer.writerow([row.id, str(row.voting_id), row.voter_id])

    return response


def import_csv(request):

    if request.user.is_staff:
        # Paso 1: obtenemos el fichero CSV

        csv_file = request.FILES['file']

        # Paso 2: verificación del fichero CSV

        if not csv_file.name.endswith('.csv'):
            return redirect("/census/addCustomCensus")

        # Paso 3: persistemos los cambios en la base de datos

        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string)

        for column in csv.reader(io_string, delimiter=',', quotechar='|'):
            _, created = Census.objects.update_or_create(
                id=column[0],
                voting_id=column[1],
                voter_id=column[2],
            )
    else:
        messages.add_message(request, messages.ERROR, internacionalize_message("Permission denied"))

    return redirect('listCensus')


# Métodos auxiliares

# Comprueba si el censo existe en la base de datos

def is_exists_census(voting_id, voter_id):
    return Census.objects.filter(voting_id=voting_id, voter_id=voter_id)

def viewVoters(request):

    users = []
    census = set(Census.objects.filter(voting_id=request.GET.get('voting_id')))

    for censo in census:

        usuario = User.objects.get(id=censo.voter_id)
        users.append(usuario)

    return render(request, "view_voters.html", {'users': users})

def passVotings(request):
    if request.user.is_staff:
        votings = Voting.objects.all()
        if votings:

            return render(request, "add_census_filtros_simples.html", {'votings': votings})

        else:
            messages.add_message(request, messages.ERROR, internacionalize_message("There are no votings available"))
            return redirect('listCensus')
    else:
        messages.add_message(request, messages.ERROR, internacionalize_message("Permission denied"))

        return redirect('listCensus')


def export_csv_view(request):

    return render(request, "export_view.html")


def import_csv_view(request):

    if request.user.is_staff:
        return render(request, "import_view.html")

    else:
        messages.add_message(request, messages.ERROR, internacionalize_message("Permission denied"))
        return redirect('listCensus')


def list_census(request):

    census = Census.objects.all()
    votings = Voting.objects.all()
    voters = User.objects.all()
    return render(request,"main_index.html",{'census': census, 'votings':votings, 'voters':voters})


def edit_census(request):

    if request.user.is_staff:
        n_id = request.GET.get('id')
        users = User.objects.all().filter(is_staff=False)
        votings = Voting.objects.all()
        census = get_object_or_404(Census,id=n_id)

        if users:
            if votings:
                return render(request, 'edit_census.html',{'census': census, 'users':users, 'votings':votings})
            else:
                messages.add_message(request, messages.ERROR, internacionalize_message("There are no votings available"))
                return redirect('listCensus')
        else:
            messages.add_message(request, messages.ERROR, internacionalize_message("There are no users available"))
            return redirect('listCensus')
    else:
        messages.add_message(request, messages.ERROR, internacionalize_message("Permission denied"))

        return redirect('listCensus')


def delete_census(request):
    if request.user.is_staff:
        n_id = request.GET.get('id')
        census = get_object_or_404(Census,id=n_id)

        return render(request, 'delete_census.html',{'census': census})
    else:
        messages.add_message(request, messages.ERROR, internacionalize_message("Permission denied"))

        return redirect('listCensus')

def save_edited_census(request):
    if request.user.is_staff:
        census_id = request.GET.get('id')
        voting_id = request.GET.get('voting_id')
        voter_id = request.GET.get('voter_id')
        census = get_object_or_404(Census,id=census_id)
        voting = get_object_or_404(Voting,id=voting_id)
        voter = get_object_or_404(User,id=voter_id)

        census.voting_id = voting_id
        census.voter_id = voter_id
        census.save()

    else:
        messages.add_message(request, messages.ERROR, internacionalize_message("Permission denied"))

    return redirect('listCensus')


def delete_selected_census(request):

    if request.user.is_staff:
        census_id = request.GET.get('id')
        census = get_object_or_404(Census,id=census_id)
        census.delete()

    else:
        messages.add_message(request, messages.ERROR, internacionalize_message("Permission denied"))

    return redirect('listCensus')
