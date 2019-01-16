from voting.models import Voting
from django.utils import timezone
from django.utils.translation import to_locale, get_language


def check_str_is_int(string):
    try:
        int(string)

        return True

    except ValueError:
        return False


def check_voting_is_started(id):

    votings = Voting.objects.filter(pk=id)
    is_started=True

    for voting in votings:
        start_date = voting.start_date

        if start_date is None:
            is_started=False

        elif start_date > timezone.now():
            is_started=False

    return is_started


def internacionalize_message(message):
    locale = to_locale(get_language())

    if locale not in ["en_US", "es", "ca"]:
        locale = "en_US"

    translations = {
        "The voting is started": {"en_US": "The voting is started",
                                  "es": "La votación ha empezado",
                                  "ca": "La votació ha començat",
                                  },
        "Invalid voting id": {"en_US": "Invalid voting id",
                              "es": "Id de votación ivalido",
                              "ca": "Id de votació invàlid",
                             },
        "Permission denied": {"en_US": "Permission denied",
                              "es": "Permiso denegado",
                              "ca": "Permís denegat",
                             },
        "No users with sex requested": {"en_US": "No users with sex requested",
                                        "es": "No hay usuarios con ese sexo",
                                        "ca": "No hi ha usuaris amb aquest sexe",
                                       },
        "No users in city requested": {"en_US": "No users in city requested",
                                       "es": "No hay usuarios con la ciudad solicitada",
                                       "ca": "No hi ha usuaris amb la ciutat sol·licitada"},
        "Age is not an integer": {"en_US": "Permission denied",
                                  "es": "Permiso denegado",
                                  "ca": "Permís denegat",
                                 },
        "There are no votings available": {"en_US": "There are no votings available",
                                           "es": "No hay votaciones disponibles",
                                           "ca": "No hi ha vots disponibles"},
        "There are no users available":{"en_US": "There are no users available",
                                        "es": "No hay usuarios disponibles",
                                        "ca": "No hi ha usuaris disponibles"},
    }

    return translations[message][locale]

