import unittest

from os.path import abspath, basename, dirname, join

import snptk.app

BASE = abspath(join(dirname(__file__), '..'))

def test_data(path):
    return join(abspath(dirname(__file__)), 'data', path)

class TestSnpTkApp(unittest.TestCase):

    def test_update_logic(self):
        snp_map = [('rs123', '6:123', 'rs456')]
        dbsnp = {'rs456': '7:123'}

        snps_to_delete, snps_to_update, coords_to_update, chromosomes_to_update = [], [('rs123', 'rs456')], [], [('rs456', '7')]

        result = snptk.app.update_logic(snp_map, dbsnp)

        self.assertEqual(result, (snps_to_delete, snps_to_update, coords_to_update, chromosomes_to_update))





