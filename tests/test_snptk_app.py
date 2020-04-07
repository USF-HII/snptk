import unittest

from collections import namedtuple
from os.path import abspath, basename, dirname, join

import snptk.app

BASE = abspath(join(dirname(__file__), '..'))

def test_data(path):
    return join(abspath(dirname(__file__)), 'data', path)

UpdateLogicOutput = namedtuple("UpdateLogicOutput", ["snps_del", "snps_up", "coords_up", "chroms_up"])
UpdateLogic_snpid_from_coord_Output = namedtuple("UpdateLogicOutput", ["snps_del", "snps_up", "multi_snps"])

class TestSnpTkAppUpdateLogic(unittest.TestCase):

    #-----------------------------------------------------------------------------------
    # update_snpid_and_position tests
    #-----------------------------------------------------------------------------------

    def test_snp_up(self):
        snp_map = [('rs123', '6:123', 'rs456')]
        dbsnp = {'rs456': '6:123'}

        expected = UpdateLogicOutput(
                snps_del=[], snps_up=[('rs123', 'rs456')], coords_up=[], chroms_up=[])

        self.assertEqual(snptk.app.update_logic_update_snpid_and_position(snp_map, dbsnp), expected)

    def test_snp_up_chrom_up(self):
        snp_map = [('rs123', '6:123', 'rs456')]
        dbsnp = {'rs456': '7:123'}

        expected = UpdateLogicOutput(
                snps_del=[], snps_up=[('rs123', 'rs456')], coords_up=[], chroms_up=[('rs456', '7')])

        self.assertEqual(snptk.app.update_logic_update_snpid_and_position(snp_map, dbsnp), expected)

    def test_no_merge_no_dbsnp(self):
        snp_map = [('rs123', '6:123', 'rs123')]
        dbsnp = {}

        expected = UpdateLogicOutput(
                snps_del=['rs123'], snps_up=[], coords_up=[], chroms_up=[])

        self.assertEqual(snptk.app.update_logic_update_snpid_and_position(snp_map, dbsnp), expected)

    def test_no_merge_history_but_in_dbsnp(self):
        snp_map = [('rs123', '6:123', 'rs123')]
        dbsnp = {'rs123': '7:456'}

        expected = UpdateLogicOutput(
                snps_del=[], snps_up=[], coords_up=[('rs123', '456')], chroms_up=[('rs123', '7')])

        self.assertEqual(snptk.app.update_logic_update_snpid_and_position(snp_map, dbsnp), expected)

    def test_snp_up_but_up_snp_already_present(self):
        snp_map = [('rs123', '6:123', 'rs456'),
                   ('rs456', '6:123', 'rs456')]

        dbsnp = {'rs123': '7:456',
                 'rs456': '6:123'}

        expected = UpdateLogicOutput(
                snps_del=['rs123'], snps_up=[], coords_up=[], chroms_up=[])

        self.assertEqual(snptk.app.update_logic_update_snpid_and_position(snp_map, dbsnp), expected)

    def test_snp_merged_but_merged_was_already_present_and_update_position(self):
        snp_map = [('rs123', '6:123', 'rs456'),
                   ('rs456', '6:123', 'rs456')]

        dbsnp = {'rs123': '7:456',
                 'rs456': '6:1000'}

        expected = UpdateLogicOutput(
                snps_del=['rs123'], snps_up=[], coords_up=[('rs456', '1000')], chroms_up=[])

        self.assertEqual(snptk.app.update_logic_update_snpid_and_position(snp_map, dbsnp), expected)

    #-----------------------------------------------------------------------------------
    # update_snpid_from_coord tests
    #-----------------------------------------------------------------------------------

    def test_k_not_in_dbsnp(self):
        bim_entries = [{
            'chromosome': '6',
            'snp_id': 'rs123',
            'distance': '0',
            'position': '1111',
            'allele_1': 'A',
            'allele_2': 'T'
             }]
        snps = ['rs123']
        dbsnp = {}
        keep_multi=False
        keep_ambig_rsids=False

        expected = UpdateLogic_snpid_from_coord_Output(
                snps_del=['rs123'], snps_up=[], multi_snps=[] )

        self.assertEqual(snptk.app.update_logic_snpid_from_coord(bim_entries, snps, dbsnp, keep_multi, keep_ambig_rsids), expected)

    def test_k_not_in_dbsnp_but_keep_ambig_rsids_true(self):
        bim_entries = [{
            'chromosome': '6',
            'snp_id': 'rs123',
            'distance': '0',
            'position': '1111',
            'allele_1': 'A',
            'allele_2': 'T'
             }]
        snps = ['rs123']
        dbsnp = {}
        keep_multi=False
        keep_ambig_rsids=True

        expected = UpdateLogic_snpid_from_coord_Output(
                snps_del=[], snps_up=[], multi_snps=[] )

        self.assertEqual(snptk.app.update_logic_snpid_from_coord(bim_entries, snps, dbsnp, keep_multi, keep_ambig_rsids), expected)

    def test_k_in_dbsnp_but_not_multi_snped_mapped_with_update(self):
        bim_entries = [{
            'chromosome': '6',
            'snp_id': 'rs123',
            'distance': '0',
            'position': '123',
            'allele_1': 'A',
            'allele_2': 'T'
             }]
        snps = ['rs123']
        dbsnp = {'6:123' :  ['rs456']}
        keep_multi=False
        keep_ambig_rsids=False

        expected = UpdateLogic_snpid_from_coord_Output(
                snps_del=[], snps_up=[('rs123', 'rs456')], multi_snps=[] )

        self.assertEqual(snptk.app.update_logic_snpid_from_coord(bim_entries, snps, dbsnp, keep_multi, keep_ambig_rsids), expected)

    def test_k_in_dbsnp_but_not_multi_snped_mapped_no_update(self):
        bim_entries = [{
            'chromosome': '6',
            'snp_id': 'rs123',
            'distance': '0',
            'position': '123',
            'allele_1': 'A',
            'allele_2': 'T'
             }]
        snps = ['rs123']
        dbsnp = {'6:123' :  ['rs123']}
        keep_multi=False
        keep_ambig_rsids=False

        expected = UpdateLogic_snpid_from_coord_Output(
                snps_del=[], snps_up=[], multi_snps=[] )

        self.assertEqual(snptk.app.update_logic_snpid_from_coord(bim_entries, snps, dbsnp, keep_multi, keep_ambig_rsids), expected)

    def test_k_in_dbsnp_multi_snped_mapped_but_keep_multi_is_false(self):
        bim_entries = [{
            'chromosome': '6',
            'snp_id': 'rs123',
            'distance': '0',
            'position': '123',
            'allele_1': 'A',
            'allele_2': 'T'
             }]
        snps = ['rs123']
        dbsnp = {'6:123' :  ['rs123', 'rs456']}
        keep_multi=False
        keep_ambig_rsids=False

        expected = UpdateLogic_snpid_from_coord_Output(
                snps_del=['rs123'], snps_up=[], multi_snps=[] )

        self.assertEqual(snptk.app.update_logic_snpid_from_coord(bim_entries, snps, dbsnp, keep_multi, keep_ambig_rsids), expected)

    def test_k_in_dbsnp_multi_snped_mapped_but_keep_multi_is_false_and_keep_ambig_rsids_true(self):
        bim_entries = [{
            'chromosome': '6',
            'snp_id': 'rs123',
            'distance': '0',
            'position': '123',
            'allele_1': 'A',
            'allele_2': 'T'
             }]
        snps = ['rs123']
        dbsnp = {'6:123' :  ['rs123', 'rs456']}
        keep_multi=False
        keep_ambig_rsids=True

        expected = UpdateLogic_snpid_from_coord_Output(
                snps_del=[], snps_up=[], multi_snps=[] )

        self.assertEqual(snptk.app.update_logic_snpid_from_coord(bim_entries, snps, dbsnp, keep_multi, keep_ambig_rsids), expected)

    def test_k_in_dbsnp_multi_snped_mapped_but_keep_multi_is_true_and_no_update(self):
        bim_entries = [{
            'chromosome': '6',
            'snp_id': 'rs123',
            'distance': '0',
            'position': '123',
            'allele_1': 'A',
            'allele_2': 'T'
             }]
        snps = ['rs123']
        dbsnp = {'6:123' :  ['rs123', 'rs456']}
        keep_multi=True
        keep_ambig_rsids=False

        expected = UpdateLogic_snpid_from_coord_Output(
                snps_del=[], snps_up=[], multi_snps=[('6:123', ['rs123', 'rs456'])] )

        self.assertEqual(snptk.app.update_logic_snpid_from_coord(bim_entries, snps, dbsnp, keep_multi, keep_ambig_rsids), expected)


    def test_k_in_dbsnp_multi_snped_mapped_but_keep_multi_is_true_with_update(self):
        bim_entries = [{
            'chromosome': '6',
            'snp_id': 'rs123',
            'distance': '0',
            'position': '123',
            'allele_1': 'A',
            'allele_2': 'T'
             }]
        snps = ['rs123']
        dbsnp = {'6:123' :  ['rs456', 'rs789']}
        keep_multi=True
        keep_ambig_rsids=False

        expected = UpdateLogic_snpid_from_coord_Output(
                snps_del=[], snps_up=[('rs123', 'rs456')], multi_snps=[('6:123', ['rs456', 'rs789'])] )

        self.assertEqual(snptk.app.update_logic_snpid_from_coord(bim_entries, snps, dbsnp, keep_multi, keep_ambig_rsids), expected)

    def test_k_in_dbsnp_multi_snped_mapped_but_keep_multi_is_true_with_no_update_but_updated_snp_already_in_bin(self):
        bim_entries = [{
            'chromosome': '6',
            'snp_id': 'rs123',
            'distance': '0',
            'position': '123',
            'allele_1': 'A',
            'allele_2': 'T'
             }]
        snps = ['rs123', 'rs456']
        dbsnp = {'6:123' :  ['rs456', 'rs789']}
        keep_multi=True
        keep_ambig_rsids=False

        expected = UpdateLogic_snpid_from_coord_Output(
                snps_del=[], snps_up=[], multi_snps=[('6:123', ['rs456', 'rs789'])] )

        self.assertEqual(snptk.app.update_logic_snpid_from_coord(bim_entries, snps, dbsnp, keep_multi, keep_ambig_rsids), expected)








