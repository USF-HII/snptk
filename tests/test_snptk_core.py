import unittest

from os.path import abspath, basename, dirname, join

import snptk.core

class TestSnpTkCore(unittest.TestCase):
    def setUp(self):
        self.test_dir = abspath(dirname(__file__))

    def test_build_bim(self):
        expected = [
            {'chromosome': '3', 'snp_id': 'rs123', 'distance': '0', 'position': '23444', 'allele_1': 'A', 'allele_2': 'C'},
            {'chromosome': '4', 'snp_id': 'rs123', 'distance': '0', 'position': '23444', 'allele_1': 'A', 'allele_2': 'C'} ]

        result = snptk.core.load_bim(join(self.test_dir, 'data/example.bim'))

        self.assertEqual(result, expected)

