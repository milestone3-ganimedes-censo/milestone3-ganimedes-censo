from datetime import date
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404, HttpResponseBadRequest
from django.core.cache import cache
from django.template.defaulttags import register

from base import mods
from django import template
from datetime import datetime

register = template.Library()

from .render import Render
from .computations import age_distribution, mean, get_sexes_percentages


class VisualizerView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            context['voting'] = r[0]
            

            # Elegimos la plantilla a renderizar en base al estado
            # de la votación
            if r[0]['start_date'] is None:
                
                # Votación no comenzada
                self.template_name = "visualizer/not_started.html"

            elif r[0]['end_date'] is None:

                # Votación en proceso
                self.template_name = "visualizer/ongoing.html"

                stats = get_statistics(vid)
                
                #Añadimos las estadísticas al contexto
                for e,v in stats.items():
                    context['stats_' + str(e)] = v

            elif r[0]['postproc'] is None and r[0]['end_date'] is not None:

                #Recuento no realizado
                self.template_name = "visualizer/not_tally.html"

            else:
                
                #Votación terminada
                self.template_name = "visualizer/ended.html"

        except Exception as e:
            print(str(e))
            raise Http404

        return context

class VisualizerPdf(TemplateView):

    def get(self, request, **kwargs):
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            voting = r[0]

            # Elegimos la plantilla a renderizar en base al estado
            # de la votación

            if r[0]['end_date'] is None:

                # Votación en proceso
                plantilla = "visualizer/ongoing_export.html"

                stats = get_statistics(vid)

                #Añadimos el prefijo stats_
                stats_formatted = {}
                for e,v in stats.items():
                    stats_formatted['stats_' + str(e)] = v

                stats_formatted['voting'] = voting

                return Render.render_pdf(plantilla, stats_formatted)

            elif r[0]['start_date'] is not None and r[0]['end_date'] is not None:
                
                #Votación terminada
                plantilla = "visualizer/ended_export.html"

                return Render.render_pdf(plantilla, {'voting':voting})
        
        except Exception as e:
            print(str(e))
            raise Http404

        return None

        

class VisualizerCsv(TemplateView):

    def get(self, request, **kwargs):
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            voting = r[0]

            # Elegimos la plantilla a renderizar en base al estado
            # de la votación

            if r[0]['end_date'] is None:

                # Votación en proceso
                plantilla = "visualizer/ongoing_export.html"

                stats = get_statistics(vid)

                #Añadimos el prefijo stats_
                stats_formatted = {}
                for e,v in stats.items():
                    stats_formatted['stats_' + str(e)] = v

                stats_formatted['voting'] = voting

                return Render.render_csv(plantilla, stats_formatted)

            elif r[0]['start_date'] is not None and r[0]['end_date'] is not None:
                
                #Votación terminada
                plantilla = "visualizer/ended_export.html"

                return Render.render_csv(plantilla, {'voting':voting})
        
        except Exception as e:
            print(str(e))
            raise Http404

        return None

class VisualizerJson(TemplateView):

    def get(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            voting = r[0]

            # Identificamos el estado de la votación
            if r[0]['start_date'] is None:
                
                return HttpResponseBadRequest()

            elif r[0]['end_date'] is None:

                # Votación en proceso
                voting_status = "ongoing"

                #Obtenemos las estadísticas de la votación
                stats = get_statistics(vid)
                stats['voting'] = voting

                return Render.render_json(voting_status, stats)

            elif r[0]['start_date'] is not None and r[0]['end_date'] is not None:
                
                # Impedir la obtención de resultados de votaciones que no han pasado
                # por tally

                if voting['postproc'] is None:
                    return HttpResponseBadRequest()

                #Votación terminada
                voting_status = 'ended'

                return Render.render_json(voting_status, {'voting':voting})

        except Exception as e:
            print(str(e))
            raise Http404

        return context
    
class VisualizerXml(TemplateView):
   
    def get(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            voting = r[0]

            # Identificamos el estado de la votación
            if r[0]['start_date'] is None:
                
                return HttpResponseBadRequest()

            elif r[0]['end_date'] is None:

                # Votación en proceso
                voting_status = "ongoing"

                #Obtenemos las estadísticas de la votación
                stats = get_statistics(vid)
                stats['voting'] = voting

                return Render.render_xml(voting_status, stats)

            elif r[0]['start_date'] is not None and r[0]['end_date'] is not None:
                
                # Impedir la obtención de resultados de votaciones que no han pasado
                # por tally

                if voting['postproc'] is None:
                    return HttpResponseBadRequest()

                #Votación terminada
                voting_status = 'ended'

                return Render.render_xml(voting_status, {'voting':voting})

        except Exception as e:
            print(str(e))
            raise Http404

        return context


class VisualizerList(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            votings = mods.get('voting')
            context['votings'] = votings

            endedVotings = []
            for voting in votings:
                if voting['end_date'] is not None:
                    endedVotings.append(voting)


            context['existsEnded'] = True if len(endedVotings) else False
            context['endedVotings'] = endedVotings

            self.template_name = "visualizer/list_ended.html"

        except Exception as e:
            print(str(e))
            raise Http404
        
        return context

STATS_NAMES = [
    'census_size',
    'voters_turnout',
    'participation_ratio',
    'voters_age_dist',
    'voters_age_mean',
    'no_voters_age_mean',
    'women_participation',
    'men_participation',
    'nonbinary_participation',
    'women_percentage',
    'men_percentage',
    'nonbinary_percentage'
]

CACHE_TIMEOUT = 20

def get_statistics(vid, counter=0):
    """ Obtiene o calcula las estadísticas dada una votación vid:int
    como un diccionario con el nombre de la estadística como 
    clave y su dato como valor."""

    #Estadísticas de la votación
    stats = {}

    #Comprobamos si las estadísticas están en caché
    cached_raw_stats = cache.get(str(vid))

    if(cached_raw_stats is None):
        # No existen las estadísticas en caché

        #Estadísticas básicas: tamaño del censo, personas que han
        #votado y participación
        census = mods.get('census', params={'voting_id': vid})
        voters_raw = mods.get('store',entry_point='/users/voting/{}/'.format(vid) )
        voters_id = [v['id'] for v in voters_raw]
        no_voters = list(set(census['voters']) - set(voters_id))

        stats['census_size'] = len(census['voters'])
        stats['voters_turnout'] = len(voters_id)
        if stats['census_size'] != 0:
            stats['participation_ratio'] = round((stats['voters_turnout'] / stats['census_size']) * 100, 2)
        else:
            stats['participation_ratio'] = 0

        contador_voters = mods.get('authentication', entry_point='/contador/', params={'list': voters_id})
        contador_no_voters = mods.get('authentication', entry_point='/contador/', params={'list': no_voters})

        voters_ages = transform_age(contador_voters['data']['all'])
        no_voters_ages = transform_age(contador_no_voters['data']['all'])
        (voters_age_dist, voters_age_mean) = age_distribution(voters_ages)
        stats['voters_age_dist'] = voters_age_dist
        stats['voters_age_mean'] = voters_age_mean
        stats['no_voters_age_mean'] = mean(no_voters_ages)

        #Estadísticas avanzadas de votación II
        contador_censo = mods.get('authentication', entry_point='/contador/', params={'list': census['voters']})
        sexes_total = transform_sexes(contador_censo['data'])

        sexes_participation = transform_sexes(contador_voters['data'])

        stats['women_participation'] = sexes_participation['W']
        stats['men_participation'] = sexes_participation['M']
        stats['nonbinary_participation'] = sexes_participation['N']

        sexes_percentages = get_sexes_percentages(sexes_participation, sexes_total)

        stats['women_percentage'] = sexes_percentages['W']
        stats['men_percentage'] = sexes_percentages['M']
        stats['nonbinary_percentage'] = sexes_percentages['N']

        #Cambiamos los valores None por 'None' (str)
        #para poder guardarlos en caché sin problemas
        processed_stats = { k: v if v is not None else 'None' for k,v in stats.items()}

        cache.set(str(vid), processed_stats, timeout=CACHE_TIMEOUT)

    else:
        #Las estadísticas deberían estar en caché...

        #Cambiamos los valores 'None' por None (NoneType)
        stats = { k: v if v != 'None' else None for k,v in cached_raw_stats.items()}

        #Si no se encuentran todas, la caché está corrupta y debemos volver
        #a calcularlas
        if stats is None or len(stats) != len(STATS_NAMES):

            #Borramos el registro actual para proceder al nuevo cálculo
            cache.delete(str(vid))
            get_statistics(vid)
    
    return stats

def transform_age(ages_raw):
    age_formated = {}
    today = date.today()

    for a in ages_raw:
        if a is None or a['date'] is None:
            continue
        birth_date = datetime.strptime(a['date'], '%Y-%m-%d')
        years = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        age_formated[years] = a['total_entries']

    return age_formated

from authentication.models import User

def transform_sexes(sexes_raw):
    
    res = {

            User.SEX_OPTIONS[0][0] : sexes_raw['man'],
            User.SEX_OPTIONS[1][0] : sexes_raw['woman'],
            User.SEX_OPTIONS[2][0] : sexes_raw['non-binary']

        }

    return res
