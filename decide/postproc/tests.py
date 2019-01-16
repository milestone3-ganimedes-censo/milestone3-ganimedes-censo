from base import mods
from postproc.models import PostProcType
from rest_framework.test import APIClient
from rest_framework.test import APITestCase


class PostProcTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)

    def tearDown(self):
        self.client = None

    def test_identity(self):
        data = {
            'type': PostProcType.IDENTITY,
            'questions': [
                {
                    'number': 1,
                    'options': [
                        {'option': 'Option 1', 'number': 1, 'votes': 5},
                        {'option': 'Option 2', 'number': 2, 'votes': 0},
                        {'option': 'Option 3', 'number': 3, 'votes': 3},
                        {'option': 'Option 4', 'number': 4, 'votes': 2},
                        {'option': 'Option 5', 'number': 5, 'votes': 5},
                        {'option': 'Option 6', 'number': 6, 'votes': 1},
                    ]
                },
                {
                    'number': 2,
                    'options': [
                        {'option': 'Option 1', 'number': 7, 'votes': 4},
                        {'option': 'Option 2', 'number': 8, 'votes': 2},
                        {'option': 'Option 3', 'number': 9, 'votes': 1},
                        {'option': 'Option 4', 'number': 10, 'votes': 1},
                        {'option': 'Option 5', 'number': 11, 'votes': 2},
                        {'option': 'Option 6', 'number': 12, 'votes': 0},
                    ],
                },
            ],
        }

        expected_result = {
            'type': PostProcType.IDENTITY,
            'questions': [
                {
                    'number': 1,
                    'options': [
                        {'option': 'Option 1', 'number': 1, 'votes': 5, 'postproc': 5},
                        {'option': 'Option 5', 'number': 5, 'votes': 5, 'postproc': 5},
                        {'option': 'Option 3', 'number': 3, 'votes': 3, 'postproc': 3},
                        {'option': 'Option 4', 'number': 4, 'votes': 2, 'postproc': 2},
                        {'option': 'Option 6', 'number': 6, 'votes': 1, 'postproc': 1},
                        {'option': 'Option 2', 'number': 2, 'votes': 0, 'postproc': 0},
                    ]
                },
                {
                    'number': 2,
                    'options': [
                        {'option': 'Option 1', 'number': 7, 'votes': 4, 'postproc': 4},
                        {'option': 'Option 2', 'number': 8, 'votes': 2, 'postproc': 2},
                        {'option': 'Option 5', 'number': 11, 'votes': 2, 'postproc': 2},
                        {'option': 'Option 3', 'number': 9, 'votes': 1, 'postproc': 1},
                        {'option': 'Option 4', 'number': 10, 'votes': 1, 'postproc': 1},
                        {'option': 'Option 6', 'number': 12, 'votes': 0, 'postproc': 0},
                    ],
                },
            ],
        }

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_seats(self):
        data = {
            'type': PostProcType.SEATS,
            'questions': [
                {
                    'number': 1,
                    'seats': 6,
                    'options': [
                        {'option': 'Option 1', 'number': 1, 'votes': 10},
                        {'option': 'Option 2', 'number': 2, 'votes': 5},
                        {'option': 'Option 3', 'number': 3, 'votes': 13},
                        {'option': 'Option 4', 'number': 4, 'votes': 2},
                    ],
                },
            ],
        }

        expected_result = {
            'type': PostProcType.SEATS,
            'questions': [
                {
                    'number': 1,
                    'seats': 6,
                    'options': [
                        {'option': 'Option 3', 'number': 3, 'votes': 13, 'postproc': 3},
                        {'option': 'Option 1', 'number': 1, 'votes': 10, 'postproc': 2},
                        {'option': 'Option 2', 'number': 2, 'votes': 5, 'postproc': 1},
                        {'option': 'Option 4', 'number': 4, 'votes': 2, 'postproc': 0},
                    ],
                },
            ],
        }

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_team(self):
        data = {
            'type': PostProcType.TEAM,
            'questions': [
                {
                    'number': 1,
                    'options': [
                        {'option': 'Option 1', 'number': 1, 'votes': 5, 'team': 0},
                        {'option': 'Option 2', 'number': 2, 'votes': 0, 'team': 1},
                        {'option': 'Option 3', 'number': 3, 'votes': 3, 'team': 0},
                        {'option': 'Option 4', 'number': 4, 'votes': 2, 'team': 1},
                        {'option': 'Option 5', 'number': 5, 'votes': 5, 'team': 2},
                        {'option': 'Option 6', 'number': 6, 'votes': 1, 'team': 3},
                    ],
                },
            ],
        }

        expected_result = {
            'type': PostProcType.TEAM,
            'questions': [
                {
                    'number': 1,
                    'options': [
                        {'option': 'Option 1', 'number': 1, 'votes': 5, 'team': 0},
                        {'option': 'Option 3', 'number': 3, 'votes': 3, 'team': 0},
                        {'option': 'Option 5', 'number': 5, 'votes': 5, 'team': 2},
                        {'option': 'Option 4', 'number': 4, 'votes': 2, 'team': 1},
                        {'option': 'Option 2', 'number': 2, 'votes': 0, 'team': 1},
                        {'option': 'Option 6', 'number': 6, 'votes': 1, 'team': 3},
                    ],
                },
            ],
        }

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_team2(self):
        data = {
            'type': PostProcType.TEAM,
            'questions': [
                {
                    'number': 1,
                    'options': [
                        {'option': 'Option 1', 'number': 1, 'votes': 1, 'team': 0},
                        {'option': 'Option 2', 'number': 2, 'votes': 0, 'team': 1},
                        {'option': 'Option 3', 'number': 3, 'votes': 0, 'team': 0},
                        {'option': 'Option 4', 'number': 4, 'votes': 0, 'team': 1},
                        {'option': 'Option 5', 'number': 5, 'votes': 0, 'team': 2},
                        {'option': 'Option 6', 'number': 6, 'votes': 0, 'team': 3},
                    ],
                },
            ],
        }

        expected_result = {
            'type': PostProcType.TEAM,
            'questions': [
                {
                    'number': 1,
                    'options': [
                        {'option': 'Option 1', 'number': 1, 'votes': 1, 'team': 0},
                        {'option': 'Option 3', 'number': 3, 'votes': 0, 'team': 0},
                        {'option': 'Option 2', 'number': 2, 'votes': 0, 'team': 1},
                        {'option': 'Option 4', 'number': 4, 'votes': 0, 'team': 1},
                        {'option': 'Option 5', 'number': 5, 'votes': 0, 'team': 2},
                        {'option': 'Option 6', 'number': 6, 'votes': 0, 'team': 3},
                    ],
                },
            ],
        }

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    # Supongamos que options es un array vacío (no hay candidatos)
    def test_parity_options_vacio(self):
        data = {
            'type': PostProcType.PARITY,
            'questions': [
                {
                    'number': 1,
                    'options': [],
                },
            ],
        }

        expected_result = {
            'type': PostProcType.PARITY,
            'questions': [
                {
                    'number': 1,
                    'options': [],
                },
            ],
        }

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)
        
    #PRUEBA BÁSICA
    def test_parity_basica(self):
        data = {
            'type': PostProcType.PARITY,
            'questions': [
                {
                    'number': 1,
                    'options': [
                        {'option': 'Option 1', 'number': 1, 'votes': 10, 'gender': True},
                        {'option': 'Option 2', 'number': 2, 'votes': 5, 'gender': True},
                        {'option': 'Option 3', 'number': 3, 'votes': 13, 'gender': False},
                        {'option': 'Option 4', 'number': 4, 'votes': 2, 'gender': False},
                    ],
                },
            ],
        }

        expected_result = {
            'type': PostProcType.PARITY,
            'questions': [
                {
                    'number': 1,
                    'options': [
                        {'option': 'Option 3', 'number': 3, 'votes': 13, 'gender': False},
                        {'option': 'Option 1', 'number': 1, 'votes': 10, 'gender': True},
                        {'option': 'Option 2', 'number': 2, 'votes': 5, 'gender': True},
                        {'option': 'Option 4', 'number': 4, 'votes': 2, 'gender': False},
                    ],
                },
            ],
        }

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    #TODOS DEL MISMO SEXO
    def test_parity_un_solo_sexo(self):
        data = {
            'type': PostProcType.PARITY,
            'questions': [
                {#Que sean todos hombres
                    'number': 1,
                    'options': [
                        {'option': 'Option 1', 'number': 1, 'votes': 10, 'gender': True},
                        {'option': 'Option 2', 'number': 2, 'votes': 5, 'gender': True},
                        {'option': 'Option 3', 'number': 3, 'votes': 13, 'gender': True},
                        {'option': 'Option 4', 'number': 4, 'votes': 2, 'gender': True},
                    ],
                },
                {#Que sean todas mujeres
                    'number': 2,
                    'options': [
                        {'option': 'Option 1', 'number': 5, 'votes': 10, 'gender': False},
                        {'option': 'Option 2', 'number': 6, 'votes': 5, 'gender': False},
                        {'option': 'Option 3', 'number': 7, 'votes': 13, 'gender': False},
                        {'option': 'Option 4', 'number': 8, 'votes': 2, 'gender': False},
                    ],
                },
            ],
        }
        expected_result = {
            'type': PostProcType.PARITY,
            'questions': [
                {#Que sean todos hombres
                    'number': 1,
                    'options': [
                        {'option': 'Option 3', 'number': 3, 'votes': 13, 'gender': True},
                        {'option': 'Option 1', 'number': 1, 'votes': 10, 'gender': True},
                        {'option': 'Option 2', 'number': 2, 'votes': 5, 'gender': True},
                        {'option': 'Option 4', 'number': 4, 'votes': 2, 'gender': True},
                    ],
                },
                {#Que sean todas mujeres
                    'number': 2,
                    'options': [
                        {'option': 'Option 3', 'number': 7, 'votes': 13, 'gender': False},
                        {'option': 'Option 1', 'number': 5, 'votes': 10, 'gender': False},
                        {'option': 'Option 2', 'number': 6, 'votes': 5, 'gender': False},
                        {'option': 'Option 4', 'number': 8, 'votes': 2, 'gender': False},
                    ],
                },
            ],
        }
        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)


    #1 CANDIDATO DE UN SEXO Y EL RESTO DEL CONTRARIO
    def test_parity_todxs_menos_unx(self):
        data = {
            'type': PostProcType.PARITY,
            'questions': [
                { #1 hombre y el resto mujeres
                    'number': 1,
                    'options': [
                        {'option': 'Option 1', 'number': 1, 'votes': 10, 'gender': True},
                        {'option': 'Option 2', 'number': 2, 'votes': 5, 'gender': False},
                        {'option': 'Option 3', 'number': 3, 'votes': 13, 'gender': False},
                        {'option': 'Option 4', 'number': 4, 'votes': 2, 'gender': False},
                    ],
                },
                {  # 1 mujer y el resto hombres
                    'number': 2,
                    'options': [
                        {'option': 'Option 1', 'number': 5, 'votes': 10, 'gender': False},
                        {'option': 'Option 2', 'number': 6, 'votes': 5, 'gender': True},
                        {'option': 'Option 3', 'number': 7, 'votes': 13, 'gender': True},
                        {'option': 'Option 4', 'number': 8, 'votes': 2, 'gender': True},
                    ],
                },

            ],
        }
        expected_result = {
            'type': PostProcType.PARITY,
            'questions': [
                {  #1 hombre y el resto mujeres
                    'number': 1,
                    'options': [
                        {'option': 'Option 3', 'number': 3, 'votes': 13, 'gender': False},
                        {'option': 'Option 1', 'number': 1, 'votes': 10, 'gender': True},
                        {'option': 'Option 2', 'number': 2, 'votes': 5, 'gender': False},
                        {'option': 'Option 4', 'number': 4, 'votes': 2, 'gender': False},
                    ],
                },
                {  # 1 mujer y el resto hombres
                    'number': 2,
                    'options': [
                        {'option': 'Option 3', 'number': 7, 'votes': 13, 'gender': True},
                        {'option': 'Option 1', 'number': 5, 'votes': 10, 'gender': False},
                        {'option': 'Option 2', 'number': 6, 'votes': 5, 'gender': True},
                        {'option': 'Option 4', 'number': 8, 'votes': 2, 'gender': True},
                    ],
                },
            ],
        }
        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_weight(self):
        data = {
            'type': PostProcType.WEIGHT,
            'questions': [
                {
                    'number': 1,
                    'options': [
                        {'option': 'Option 1', 'number': 1, 'votes': 5, 'weight': 5},
                        {'option': 'Option 2', 'number': 2, 'votes': 0, 'weight': 5},
                        {'option': 'Option 3', 'number': 3, 'votes': 3, 'weight': 5},
                        {'option': 'Option 4', 'number': 4, 'votes': 2, 'weight': 5},
                        {'option': 'Option 5', 'number': 5, 'votes': 5, 'weight': 5},
                        {'option': 'Option 6', 'number': 6, 'votes': 1, 'weight': 5},
                    ],
                },
            ],
        }

        expected_result = {
            'type': PostProcType.WEIGHT,
            'questions': [
                {
                    'number': 1,
                    'options': [
                        {'option': 'Option 1', 'number': 1, 'votes': 5, 'weight': 5, 'postproc': 25},
                        {'option': 'Option 5', 'number': 5, 'votes': 5, 'weight': 5, 'postproc': 25},
                        {'option': 'Option 3', 'number': 3, 'votes': 3, 'weight': 5, 'postproc': 15},
                        {'option': 'Option 4', 'number': 4, 'votes': 2, 'weight': 5, 'postproc': 10},
                        {'option': 'Option 6', 'number': 6, 'votes': 1, 'weight': 5, 'postproc': 5},
                        {'option': 'Option 2', 'number': 2, 'votes': 0, 'weight': 5, 'postproc': 0},
                    ],
                },
            ],
        }

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    # campo weight con 0
    def test_weight2(self):
        data = {
            'type': PostProcType.WEIGHT,
            'questions': [
                {
                    'number': 1,
                    'options': [
                        {'option': 'Option 1', 'number': 1, 'votes': 5, 'weight': 0},
                        {'option': 'Option 2', 'number': 2, 'votes': 0, 'weight': 5},
                        {'option': 'Option 3', 'number': 3, 'votes': 3, 'weight': 4},
                        {'option': 'Option 4', 'number': 4, 'votes': 2, 'weight': 3},
                        {'option': 'Option 5', 'number': 5, 'votes': 5, 'weight': 2},
                        {'option': 'Option 6', 'number': 6, 'votes': 1, 'weight': 1},
                    ],
                },
            ],
        }

        expected_result = {
            'type': PostProcType.WEIGHT,
            'questions': [
                {
                    'number': 1,
                    'options': [
                        {'option': 'Option 3', 'number': 3, 'votes': 3, 'weight': 4, 'postproc': 12},
                        {'option': 'Option 5', 'number': 5, 'votes': 5, 'weight': 2, 'postproc': 10},
                        {'option': 'Option 4', 'number': 4, 'votes': 2, 'weight': 3, 'postproc': 6},
                        {'option': 'Option 6', 'number': 6, 'votes': 1, 'weight': 1, 'postproc': 1},
                        {'option': 'Option 1', 'number': 1, 'votes': 5, 'weight': 0, 'postproc': 0},
                        {'option': 'Option 2', 'number': 2, 'votes': 0, 'weight': 5, 'postproc': 0},
                    ],
                },
            ],
        }

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    #Valores muy altos en el campo weight
    def test_weight3(self):
        data = {
            'type': PostProcType.WEIGHT,
            'questions': [
                {
                    'number': 1,
                    'options': [
                        {'option': 'Option 1', 'number': 1, 'votes': 6, 'weight': 10000},
                        {'option': 'Option 2', 'number': 2, 'votes': 0, 'weight': 20000},
                        {'option': 'Option 3', 'number': 3, 'votes': 3, 'weight': 40000},
                        {'option': 'Option 4', 'number': 4, 'votes': 2, 'weight': 50000},
                        {'option': 'Option 5', 'number': 5, 'votes': 5, 'weight': 10000},
                        {'option': 'Option 6', 'number': 6, 'votes': 1, 'weight': 300},
                    ],
                },
            ],
        }
        expected_result = {
            'type': PostProcType.WEIGHT,
            'questions': [
                {
                    'number': 1,
                    'options': [
                        {'option': 'Option 3', 'number': 3, 'votes': 3, 'weight': 40000, 'postproc': 120000},
                        {'option': 'Option 4', 'number': 4, 'votes': 2, 'weight': 50000, 'postproc': 100000},
                        {'option': 'Option 1', 'number': 1, 'votes': 6, 'weight': 10000, 'postproc': 60000},
                        {'option': 'Option 5', 'number': 5, 'votes': 5, 'weight': 10000, 'postproc': 50000},
                        {'option': 'Option 6', 'number': 6, 'votes': 1, 'weight': 300, 'postproc': 300},
                        {'option': 'Option 2', 'number': 2, 'votes': 0, 'weight': 20000, 'postproc': 0},
                    ],
                },
            ],
        }

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

        #Test con el campo weight en negativo
        def test_weight4(self):
            data = {
                'type': PostProcType.WEIGHT,
                'questions': [
                    {
                        'number': 1,
                        'options': [
                            {'option': 'Option 1', 'number': 1, 'votes': 5, 'weight': -5},
                            {'option': 'Option 2', 'number': 2, 'votes': 0, 'weight': 5},
                            {'option': 'Option 3', 'number': 3, 'votes': 3, 'weight': 5},
                            {'option': 'Option 4', 'number': 4, 'votes': 2, 'weight': 5},
                            {'option': 'Option 5', 'number': 5, 'votes': 5, 'weight': 5},
                            {'option': 'Option 6', 'number': 6, 'votes': 1, 'weight': -5},
                        ],
                    },
                ],
            }

            expected_result = {
                'type': PostProcType.WEIGHT,
                'questions': [
                    {
                        'number': 1,
                        'options': [
                            {'option': 'Option 5', 'number': 5, 'votes': 5, 'weight': 5, 'postproc': 25},
                            {'option': 'Option 3', 'number': 3, 'votes': 3, 'weight': 5, 'postproc': 15},
                            {'option': 'Option 4', 'number': 4, 'votes': 2, 'weight': 5, 'postproc': 10},
                            {'option': 'Option 2', 'number': 2, 'votes': 0, 'weight': 5, 'postproc': 0},
                            {'option': 'Option 6', 'number': 6, 'votes': 1, 'weight': 5, 'postproc': -5},
                            {'option': 'Option 1', 'number': 1, 'votes': 5, 'weight': 5, 'postproc': -25},
                        ],
                    },
                ],
            }

            response = self.client.post('/postproc/', data, format='json')
            self.assertEqual(response.status_code, 200)

            values = response.json()
            self.assertEqual(values, expected_result)
