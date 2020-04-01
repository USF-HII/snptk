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

    #def test_update_snp_id_snphistory_and_rsmerge(self):
    #    snpid =  'rs397507451'
    #    snp_history = {'397507451'}
    #    rsmerge = {'397507451': ('386829069', '386829069')}

    #    self.assertEqual(snptk.core.update_snp_id(snpid, snp_history, rsmerge), 'rs386829069')

    #def test_update_snp_id_no_snphistory_or_rsmerge(self):
    #    snpid =  'rs123'
    #    snp_history = {}
    #    rsmerge = {}

    #    self.assertEqual(snptk.core.update_snp_id(snpid, snp_history, rsmerge), "rs123")

    #def test_update_snp_id_snp_history_only(self):
    #    snpid =  'rs123'
    #    snp_history = set(['123'])
    #    rsmerge = {}

    #    self.assertEqual(snptk.core.update_snp_id(snpid, snp_history, rsmerge), None)

    def test_update_snp_id_new_logic_rsmerge_only_one_merge(self):
        snpid =  'rs123'
        rsmerge = {'123': '456'}

        self.assertEqual(snptk.core.update_snp_id(snpid, rsmerge), 'rs456')

    def test_update_snp_id_new_logic_rsmerge_only_mutiple_merges(self):
        snpid =  'rs123'
        rsmerge = {'123': '456',
                   '456': '789',
                   '789': '000'
                }

        self.assertEqual(snptk.core.update_snp_id(snpid, rsmerge), 'rs000')
