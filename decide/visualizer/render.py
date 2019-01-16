from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
import csv
import json
import xml.etree.ElementTree as ET
from wsgiref.util import FileWrapper
from xml.dom.minidom import *


class Render:

    def render_pdf(path, params):
        plantilla = get_template(path)
        html = plantilla.render(params)

        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)

        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type='application/pdf')
        
        else:
            return HttpResponse("Error renderizando el archivo PDF", status=400)

    def render_csv(path, params):
        response = HttpResponse(content_type='text/csv', charset='UTF-8')
        response['Content-Disposition'] = 'attachment; filename="resultados.csv"'

        votacion = params['voting']
        writer = csv.writer(response)
        print(votacion)

        if path == 'visualizer/ended_export.html':
            
            writer.writerow([votacion['name']])
            writer.writerow(['Resultados'])

            for q in votacion['questions']:
                writer.writerow([q['number'], q['desc']])

                if votacion['postproc']['type'] == 1 or votacion['postproc']['type'] == 2:
                    writer.writerow(['Opción', 'Total', 'Número de votos'])

                elif votacion['postproc']['type'] == 3:
                    writer.writerow(['Género', 'Opción', 'Número de votos'])
                
                elif votacion['postproc']['type'] == 4:
                    writer.writerow(['Equipo', 'Opción', 'Número de votos'])

                else:
                    writer.writerow(['Opción', 'Número de votos'])


                for p in votacion['postproc']['questions']:
                    if p['number'] == q['number']:
                        for o in p['options']:

                            if votacion['postproc']['type'] == 1 or votacion['postproc']['type'] == 2:
                                writer.writerow([o['option'], o['postproc'], o['votes']])

                            elif votacion['postproc']['type'] == 3:
                                gender = "Hombre" if o['gender'] == True else "Mujer"
                                writer.writerow([gender, o['option'], o['votes']])

                            elif votacion['postproc']['type'] == 4:
                                writer.writerow([o['team'], o['option'], o['votes']])
                            
                            else:
                                writer.writerow([o['option'], o['postproc']])
        
        elif path == 'visualizer/ongoing_export.html':

            writer.writerow([votacion['name']])
            writer.writerow(['Votación en curso'])

            writer.writerow(['Estadísticas'])
            writer.writerow(['Tamaño del censo', str(params['stats_census_size'])])
            writer.writerow(['Personas que han votado', str(params['stats_voters_turnout'])])
            writer.writerow(['Porcentaje de participación', str(params['stats_participation_ratio']) + '%'])

            if params['stats_voters_age_mean']:
                writer.writerow(['Edad media de las personas que han votado', str(params['stats_voters_age_mean']) + ' años'])

            if params['stats_no_voters_age_mean']:
                writer.writerow(['Edad media de las personas que no han votado', str(params['stats_no_voters_age_mean']) + ' años'])
            
            writer.writerow(['Análisis de la participación según rango etario'])

            for rango, cantidad in params['stats_voters_age_dist'].items():
                writer.writerow([str(rango) + ' años', str(cantidad) + '%'])

            writer.writerow(['Número de mujeres que han votado', str(params['stats_women_participation'])])
            writer.writerow(['Porcentaje de mujeres que han votado respecto a su total', str(params['stats_women_percentage']) + '%'])
            writer.writerow(['Número de personas de género no binario que han votado', str(params['stats_nonbinary_participation'])])
            writer.writerow(['Porcentaje de personas de género no binario que han votado respecto a su total', str(params['stats_nonbinary_percentage']) + '%'])
            writer.writerow(['Número de hombres que han votado', str(params['stats_men_participation'])])
            writer.writerow(['Porcentaje de hombres que han votado respecto a su total', str(params['stats_men_percentage']) + '%'])

        return response

    def render_json(voting_status, params):
        
        response = HttpResponse(content_type='application/json', charset='UTF-8')
        response['Content-Disposition'] = 'attachment; filename="resultados.json"'

        votacion = params['voting']

        if voting_status == 'ended':
            
            export = {}
            results_main = {}

            # Descripción del informe
            results_description = {}
            results_description['Votación'] = votacion['name']
            if votacion['desc']:
                results_description['Descripción'] = votacion['desc']
            results_description['Id'] = votacion['id']

            # Resultados
            resultados = votacion['postproc']
            preguntas = {}
            
            for i,q in enumerate(resultados['questions']):
                results_results = {}

                for r in q['options']:

                    if resultados['type'] == 0:
                        results_results[str(r['option'])] = "Número de votos: {}".format(r['postproc'])
                    elif resultados['type'] == 1 or resultados['type'] == 2:
                        results_results[str(r['option'])] = "Total: {} - Número de votos: {}".format(r['postproc'], r['votes'])
                    elif resultados['type'] == 3:
                        genero = "Hombre" if r['gender'] else "Mujer"
                        results_results[str(r['option'])] = " ({}) - Número de votos: {}".format(genero, r['votes'])
                    elif resultados['type'] == 4:
                         results_results['Equipo ' + str(r['team']) + " - " + str(r['option'])] = "Número de votos: {}".format(r['votes'])
                    else:
                        results_results[str(r['option'])] = r['votes']
                
                preguntas[str(votacion['questions'][i]['desc'])] = results_results
            
            # Composición de la jerarquía
            results_main['Información de la Votación'] = results_description
            results_main['Resultados por Pregunta'] = preguntas

            export['Informe de Resultados'] = results_main

            json.dump(export, response)
        
        elif voting_status == 'ongoing':
            
            export = {}
            stats_main = {}

            # Descripción del informe
            stats_description = {}
            stats_description['Votación'] = votacion['name']
            if votacion['desc']:
                stats_description['Descripción'] = votacion['desc']
            stats_description['Id'] = votacion['id']

            #Estadísticas básicas de una votación
            stats_basicas = {}
            stats_basicas['Tamaño del censo'] = str(params['census_size'])
            stats_basicas['Personas que han votado'] = str(params['voters_turnout'])
            stats_basicas['Porcentaje de participación'] = str(params['participation_ratio']) + '%'

            #Estadísticas de edad
            stats_edad = {}
            if params['voters_age_mean']:
                stats_edad['Edad media de las personas que han votado'] = str(params['voters_age_mean']) + ' años'

            if params['no_voters_age_mean']:
                stats_edad['Edad media de las personas que no han votado'] =  str(params['no_voters_age_mean']) + ' años'
            
            #Estadísticas por rango etario
            stats_edad_rango = {} 
            
            for rango, cantidad in params['voters_age_dist'].items():
                stats_edad_rango[str(rango) + ' años'] =  str(cantidad) + '%'

            #Estadísticas por género
            stats_genero = {}
            
            stats_genero['Número de mujeres que han votado'] = str(params['women_participation'])
            stats_genero['Porcentaje de mujeres que han votado respecto a su total'] = str(params['women_percentage']) + '%'
            stats_genero['Número de personas de género no binario que han votado'] = str(params['nonbinary_participation'])
            stats_genero['Porcentaje de personas de género no binario que han votado respecto a su total'] = str(params['nonbinary_percentage']) + '%'
            stats_genero['Número de hombres que han votado'] = str(params['men_participation'])
            stats_genero['Porcentaje de hombres que han votado respecto a su total'] = str(params['men_percentage']) + '%'

            #Composición de la jerarquía
            stats_edad['Análisis de la participación según rango etario'] = stats_edad_rango
            stats_main['Información de la Votación'] = stats_description
            stats_main['Estadísticas básicas de una votación'] = stats_basicas
            stats_main['Estadísticas basadas en la edad'] = stats_edad
            stats_main['Estadísticas basadas en el género'] = stats_genero

            export['Estadísticas'] = stats_main

            json.dump(export, response)

        return response

    def render_xml(voting_status, params):

        response = HttpResponse(content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename="resultados.xml"'

        votacion = params['voting']

        if voting_status == 'ended':
            # Creación del XML 

            #Descripción del informe
            voting = ET.Element("voting")
            name = ET.SubElement(voting, 'name')
            name.text = votacion['name']
            desc = ET.SubElement(voting, 'description')
            desc.text = votacion['desc']
            id = ET.SubElement(voting, 'id')
            id.text = str(votacion['id'])

            #Resultados
            results = ET.SubElement(voting, "results")
            questions = votacion['postproc']['questions']

            for q in questions:
                pregunta = votacion['questions'][q['number']-1]

                question = ET.SubElement(results, 'question')
                desc = ET.SubElement(question, 'desc')
                desc.text = pregunta['desc']
                number = ET.SubElement(question, 'number')
                number.text = str(q['number'])
                options = ET.SubElement(question, 'options')
                for o in q['options']:
                    option = ET.SubElement(options, 'option')
                    desc = ET.SubElement(option, 'desc')
                    desc.text = o['option']
                    if(votacion['postproc']['type'] == 1 or votacion['postproc']['type'] == 2):
                        postproc = ET.SubElement(option, 'postproc')
                        postproc.text = str(o['postproc'])
                        votes = ET.SubElement(option, 'votes')
                        votes.text = str(o['votes'])
                    elif(votacion['postproc']['type'] == 3):
                        if(o['gender']==True):
                            gender = ET.SubElement(option, 'gender')
                            gender.text = "Male"
                        else:
                            gender = ET.SubElement(option, 'gender')
                            gender.text = "Female"
                        votes = ET.SubElement(option, 'votes')
                        votes.text = str(o['votes'])
                    elif(votacion['postproc']['type'] == 4):
                        team = ET.SubElement(option, 'team')
                        team.text = str(o['team'])
                        votes = ET.SubElement(option, 'votes')
                        votes.text = str(o['votes'])
                    else:
                        postproc = ET.SubElement(option, 'postproc')
                        postproc.text = str(o['postproc'])


            #Pasar el XML a String
            mydata = ET.tostring(voting)

            #Añadirlo al response
            dom = parseString(mydata)
            dom.toprettyxml(encoding='UTF-8')
            dom.writexml(response)  
        
        elif voting_status == 'ongoing':
            
            # Creación del XML 

            #Descripción del informe
            voting = ET.Element("voting")
            name = ET.SubElement(voting, 'name')
            name.text = votacion['name']
            desc = ET.SubElement(voting, 'description')
            desc.text = votacion['desc']
            id = ET.SubElement(voting, 'id')
            id.text = str(votacion['id'])

            #Estadisticas
            stats = ET.SubElement(voting, 'stats')

            #Estadísticas básicas de una votación

            basics = ET.SubElement(stats, 'basics')
            censusSize = ET.SubElement(basics, 'censusSize')
            censusSize.text = str(params['census_size'])
            numVotes = ET.SubElement(basics, 'numVotes')
            numVotes.text =  str(params['voters_turnout'])
            participationRatio = ET.SubElement(basics, 'participationRatio')
            participationRatio.text = str(params['participation_ratio']) + '%'


            #Estadísticas de edad
            age = ET.SubElement(stats, 'byAge')
            if params['voters_age_mean']:
                votersAgeMean = ET.SubElement(age, 'votersAgeMean')
                votersAgeMean.text = str(params['voters_age_mean']) + ' years'

            if params['no_voters_age_mean']:
                noVotersAgeMean = ET.SubElement(age, 'noVotersAgeMean')
                noVotersAgeMean.text =  str(params['no_voters_age_mean']) + ' years'
            
            #Estadísticas por rango etario
            ageRange = ET.SubElement(stats, 'byAgeRange')
            
            for rango, cantidad in params['voters_age_dist'].items():
                age = ET.SubElement(ageRange, 'age')
                value = ET.SubElement(age, 'value')
                value.text = str(rango) + ' años'
                quantity = ET.SubElement(age, 'quantity')
                quantity.text = str(cantidad) + '%'

            #Estadísticas por género
            genre = ET.SubElement(stats, "byGenre")
            
            numWomen = ET.SubElement(genre, 'numWomen')
            numWomen.text = str(params['women_participation'])
            ratioWomen = ET.SubElement(genre, 'ratioWomen')
            ratioWomen.text = str(params['women_percentage']) + '%'
            nonBinary = ET.SubElement(genre, 'nonBinary')
            nonBinary.text = str(params['nonbinary_participation'])
            ratioNonBinary = ET.SubElement(genre, 'ratioNonBinary')
            ratioNonBinary.text = str(params['nonbinary_percentage']) + '%'
            numMen = ET.SubElement(genre, 'numMen')
            numMen.text = str(params['men_participation'])
            ratioMen = ET.SubElement(genre, 'ratioMen')
            ratioMen.text = str(params['men_percentage']) + '%'

            #Pasar el XML a String
            mydata = ET.tostring(voting)

            #Añadirlo al response
            dom = parseString(mydata)
            dom.toprettyxml()
            dom.writexml(response)

        return response

      