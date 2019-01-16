from base import mods
from django.test import TestCase
from .computations import AGE_RANGES, age_distribution

import statistics

class VisualizerTestCase(TestCase):

    def test_age_distribution_driver(self):

        # Conjunto arbitrario de datos referentes a edades
        data = {1:1, 99:1, 45:1, 16:1, 39:1, 22:1, 63:1}

        # Conjunto de adades vacío
        data_empty = {}

        # Conjunto con edades con 0's
        data_with_zeros = {0:5, 63:1}

        # Conjunto de adades con 0's exlusivamente
        data_zeros = {0:100}

        # Conjunto arbitrario de datos con edades repetidas
        data_repeated = {1:1, 25:5}

        self.age_distribution_template(data)
        self.age_distribution_template(data_empty)
        self.age_distribution_template(data_with_zeros)
        self.age_distribution_template(data_zeros)
        self.age_distribution_template(data_repeated)


    def age_distribution_template(self, data):

        contar_elem = lambda x, x_min, x_max: sum([1 for e in x if e > x_min and e <= x_max])
        tam = sum(data.values())
        repeated_data = []

        for age, number in data.items():
            for _ in range(0,number):
                repeated_data.append(age)

        expected_distribution = AGE_RANGES.copy()
        for (x_min, x_max) in AGE_RANGES.keys():
            expected_distribution[(x_min,x_max)] = 0 if tam == 0 else round(100 * contar_elem(repeated_data,
             x_min, x_max)/tam,2)

        expected_mean = None if len(data) == 0 else round(statistics.mean(repeated_data), 2)
        calc_dist, calc_mean = age_distribution(data)

        self.assertEqual(len(calc_dist), len(expected_distribution))

        for (e, o) in zip(expected_distribution.values(), calc_dist.values()):
            self.assertAlmostEqual(e, o, places=1)
        
        self.assertEqual(expected_mean, calc_mean)
