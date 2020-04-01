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

    # no merge history and not in dbsnp
    def test_update_logic_2(self):
        snp_map = [('rs123', '6:123', 'rs123')]
        dbsnp = {}

        snps_to_delete, snps_to_update, coords_to_update, chromosomes_to_update = ['rs123'], [], [], []

        result = snptk.app.update_logic(snp_map, dbsnp)

        self.assertEqual(result, (snps_to_delete, snps_to_update, coords_to_update, chromosomes_to_update))

    def test_update_logic_no_merge_history_but_in_dbsnp(self):
        snp_map = [('rs123', '6:123', 'rs123')]
        dbsnp = {'rs123': '7:456'}

        snps_to_delete, snps_to_update, coords_to_update, chromosomes_to_update = [], [], [('rs123', '456')], [('rs123', '7')]

        result = snptk.app.update_logic(snp_map, dbsnp)

        self.assertEqual(result, (snps_to_delete, snps_to_update, coords_to_update, chromosomes_to_update))

    # if snp_id_new in [snp[0] for snp in snp_map]:
    def test_update_logic_4(self):
        snp_map = [('rs123', '6:123', 'rs456'), ('rs456', '6:123', 'rs456')]
        dbsnp = {'rs123': '7:456', 'rs456': '6:123'}

        snps_to_delete, snps_to_update, coords_to_update, chromosomes_to_update = ['rs123'], [], [], []

        result = snptk.app.update_logic(snp_map, dbsnp)

        self.assertEqual(result, (snps_to_delete, snps_to_update, coords_to_update, chromosomes_to_update))

    def test_update_logic_when_snp_merged_but_merged_was_already_present_and_update_position(self):
        snp_map = [('rs123', '6:123', 'rs456'), ('rs456', '6:123', 'rs456')]
        dbsnp = {'rs123': '7:456', 'rs456': '6:1000'}

        snps_to_delete, snps_to_update, coords_to_update, chromosomes_to_update = ['rs123'], [], [('rs456', '1000')], []

        result = snptk.app.update_logic(snp_map, dbsnp)

        self.assertEqual(result, (snps_to_delete, snps_to_update, coords_to_update, chromosomes_to_update))
