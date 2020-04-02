import unittest

from collections import namedtuple
from os.path import abspath, basename, dirname, join

import snptk.app

BASE = abspath(join(dirname(__file__), '..'))

def test_data(path):
    return join(abspath(dirname(__file__)), 'data', path)

UpdateLogicOutput = namedtuple("UpdateLogicOutput", ["snps_del", "snps_up", "coords_up", "chroms_up"])

class TestSnpTkAppUpdateLogic(unittest.TestCase):

    def test_snp_up(self):
        snp_map = [('rs123', '6:123', 'rs456')]
        dbsnp = {'rs456': '6:123'}

        expected = UpdateLogicOutput(
                snps_del=[], snps_up=[('rs123', 'rs456')], coords_up=[], chroms_up=[])

        self.assertEqual(snptk.app.update_logic(snp_map, dbsnp), expected)

    def test_snp_up_chrom_up(self):
        snp_map = [('rs123', '6:123', 'rs456')]
        dbsnp = {'rs456': '7:123'}

        expected = UpdateLogicOutput(
                snps_del=[], snps_up=[('rs123', 'rs456')], coords_up=[], chroms_up=[('rs456', '7')])

        self.assertEqual(snptk.app.update_logic(snp_map, dbsnp), expected)

    def test_no_merge_no_dbsnp(self):
        snp_map = [('rs123', '6:123', 'rs123')]
        dbsnp = {}

        expected = UpdateLogicOutput(
                snps_del=['rs123'], snps_up=[], coords_up=[], chroms_up=[])

        self.assertEqual(snptk.app.update_logic(snp_map, dbsnp), expected)

    def test_no_merge_history_but_in_dbsnp(self):
        snp_map = [('rs123', '6:123', 'rs123')]
        dbsnp = {'rs123': '7:456'}

        expected = UpdateLogicOutput(
                snps_del=[], snps_up=[], coords_up=[('rs123', '456')], chroms_up=[('rs123', '7')])

        self.assertEqual(snptk.app.update_logic(snp_map, dbsnp), expected)

    def test_snp_up_but_up_snp_already_present(self):
        snp_map = [('rs123', '6:123', 'rs456'),
                   ('rs456', '6:123', 'rs456')]

        dbsnp = {'rs123': '7:456',
                 'rs456': '6:123'}

        expected = UpdateLogicOutput(
                snps_del=['rs123'], snps_up=[], coords_up=[], chroms_up=[])

        self.assertEqual(snptk.app.update_logic(snp_map, dbsnp), expected)

    def test_snp_merged_but_merged_was_already_present_and_update_position(self):
        snp_map = [('rs123', '6:123', 'rs456'),
                   ('rs456', '6:123', 'rs456')]

        dbsnp = {'rs123': '7:456',
                 'rs456': '6:1000'}

        expected = UpdateLogicOutput(
                snps_del=['rs123'], snps_up=[], coords_up=[('rs456', '1000')], chroms_up=[])

        self.assertEqual(snptk.app.update_logic(snp_map, dbsnp), expected)
