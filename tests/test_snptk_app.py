import unittest

from collections import namedtuple
from os.path import abspath, basename, dirname, join

import snptk.app

BASE = abspath(join(dirname(__file__), '..'))

def test_data(path):
    return join(abspath(dirname(__file__)), 'data', path)

UpdateLogicOutput = namedtuple("UpdateLogicOutput", ["snps_del", "snps_up", "coords_up", "chroms_up"])

UpdateLogic_map_using_coord_Output = namedtuple("UpdateLogicOutput", ["snps_del", "snps_up", "multi_snps"])

class TestSnpTkAppUpdateLogicUpdateSnpIdAndPosition(unittest.TestCase):

    #-----------------------------------------------------------------------------------
    # update_snpid_and_position tests
    #-----------------------------------------------------------------------------------

    def test_snp_up(self):
        snp_map = [('rs123', '6:123', 'rs456')]
        dbsnp = {'rs456': '6:123'}
        unmappable_snps = set()

        expected = UpdateLogicOutput(
                snps_del=[], snps_up=[('rs123', 'rs456')], coords_up=[], chroms_up=[])

        self.assertEqual(snptk.app.map_using_rs_id_logic(snp_map, dbsnp, unmappable_snps), expected)

    def test_snp_up_chrom_up(self):
        snp_map = [('rs123', '6:123', 'rs456')]
        dbsnp = {'rs456': '7:123'}
        unmappable_snps = set()

        expected = UpdateLogicOutput(
                snps_del=[], snps_up=[('rs123', 'rs456')], coords_up=[], chroms_up=[('rs456', '7')])

        self.assertEqual(snptk.app.map_using_rs_id_logic(snp_map, dbsnp, unmappable_snps), expected)

    def test_no_merge_no_dbsnp(self):
        snp_map = [('rs123', '6:123', 'rs123')]
        dbsnp = {}
        unmappable_snps = set()

        expected = UpdateLogicOutput(
                snps_del=['rs123'], snps_up=[], coords_up=[], chroms_up=[])

        self.assertEqual(snptk.app.map_using_rs_id_logic(snp_map, dbsnp, unmappable_snps), expected)

    def test_no_merge_history_but_in_dbsnp(self):
        snp_map = [('rs123', '6:123', 'rs123')]
        dbsnp = {'rs123': '7:456'}
        unmappable_snps = set()

        expected = UpdateLogicOutput(
                snps_del=[], snps_up=[], coords_up=[('rs123', '456')], chroms_up=[('rs123', '7')])

        self.assertEqual(snptk.app.map_using_rs_id_logic(snp_map, dbsnp, unmappable_snps), expected)

    def test_snp_up_but_up_snp_already_present(self):
        snp_map = [('rs123', '6:123', 'rs456'),
                   ('rs456', '6:123', 'rs456')]

        dbsnp = {'rs123': '7:456',
                 'rs456': '6:123'}

        unmappable_snps = set()

        expected = UpdateLogicOutput(
                snps_del=['rs123'], snps_up=[], coords_up=[], chroms_up=[])

        self.assertEqual(snptk.app.map_using_rs_id_logic(snp_map, dbsnp, unmappable_snps), expected)

    def test_snp_merged_but_merged_was_already_present_and_update_position(self):
        snp_map = [('rs123', '6:123', 'rs456'),
                   ('rs456', '6:123', 'rs456')]

        dbsnp = {'rs123': '7:456',
                 'rs456': '6:1000'}

        unmappable_snps = set()

        expected = UpdateLogicOutput(
                snps_del=['rs123'], snps_up=[], coords_up=[('rs456', '1000')], chroms_up=[])

        self.assertEqual(snptk.app.map_using_rs_id_logic(snp_map, dbsnp, unmappable_snps), expected)

    def test_include_file_no_merge(self):
        snp_map = [('rs456', '6:123', 'rs456')]

        dbsnp = {'rs123': '7:456'}

        unmappable_snps = {'rs456'}

        expected = UpdateLogicOutput(
                snps_del=[], snps_up=[], coords_up=[], chroms_up=[])

        self.assertEqual(snptk.app.map_using_rs_id_logic(snp_map, dbsnp, unmappable_snps), expected)

    def test_include_file_merge(self):
        snp_map = [('rs456', '6:123', 'rs789')]

        dbsnp = {'rs123': '7:456'}

        unmappable_snps = {'rs789'}

        expected = UpdateLogicOutput(
                snps_del=[], snps_up=[('rs456', 'rs789')], coords_up=[], chroms_up=[])

        self.assertEqual(snptk.app.map_using_rs_id_logic(snp_map, dbsnp, unmappable_snps), expected)

class TestSnpTkAppUpdateLogicSnpIdFromCoord(unittest.TestCase):
    def setUp(self):
        self.bim_entries = [{
            'chromosome': '6',
            'snp_id': 'rs123',
            'distance': '0',
            'position': '123',
            'allele_1': 'A',
            'allele_2': 'T'
             }]

        self.bim_entries_no_rs = [{
            'chromosome': '6',
            'snp_id': '123',
            'distance': '0',
            'position': '123',
            'allele_1': 'A',
            'allele_2': 'T'
             }]

    def test_not_in_dbsnp(self):
        snps = ['rs123']
        dbsnp = {}
        keep_multi = False
        keep_unmapped_rsids = False

        expected = UpdateLogic_map_using_coord_Output(
                snps_del=['rs123'], snps_up=[], multi_snps=[] )

        self.assertEqual(snptk.app.map_using_coord_logic(self.bim_entries, snps, dbsnp, keep_multi, keep_unmapped_rsids), expected)

    def test_not_in_dbsnp_keep_unmapped_rsids(self):
        snps = ['rs123']
        dbsnp = {}
        keep_multi = False
        keep_unmapped_rsids = True

        expected = UpdateLogic_map_using_coord_Output(
                snps_del=[], snps_up=[], multi_snps=[] )

        self.assertEqual(snptk.app.map_using_coord_logic(self.bim_entries, snps, dbsnp, keep_multi, keep_unmapped_rsids), expected)

    def test_update_snp(self):
        """
        Inside of dbsnp but not multi mapped to mutiple snps

        6:123 maps to only rs456 inside of dbsnp
        """
        snps = ['rs123']
        dbsnp = {'6:123' :  ['rs456']}
        keep_multi = False
        keep_unmapped_rsids = False

        expected = UpdateLogic_map_using_coord_Output(
                snps_del=[], snps_up=[('rs123', 'rs456')], multi_snps=[] )

        self.assertEqual(snptk.app.map_using_coord_logic(self.bim_entries, snps, dbsnp, keep_multi, keep_unmapped_rsids), expected)

    def test_no_update(self):
        snps = ['rs123']
        dbsnp = {'6:123' :  ['rs123']}
        keep_multi = False
        keep_unmapped_rsids = False

        expected = UpdateLogic_map_using_coord_Output(
                snps_del=[], snps_up=[], multi_snps=[] )

        self.assertEqual(snptk.app.map_using_coord_logic(self.bim_entries, snps, dbsnp, keep_multi, keep_unmapped_rsids), expected)

    def test_multi_snp_unmapped_rsids_false(self):
        snps = ['rs123']
        dbsnp = {'6:123' :  ['rs123', 'rs456']}
        keep_multi = False
        keep_unmapped_rsids = False

        expected = UpdateLogic_map_using_coord_Output(
                snps_del=['rs123'], snps_up=[], multi_snps=[] )

        self.assertEqual(snptk.app.map_using_coord_logic(self.bim_entries, snps, dbsnp, keep_multi, keep_unmapped_rsids), expected)

    def test_unmapped_rsids(self):
        snps = ['rs123']
        dbsnp = {'6:123' :  ['rs123', 'rs456']}
        keep_multi = False
        keep_unmapped_rsids = True

        expected = UpdateLogic_map_using_coord_Output(
                snps_del=[], snps_up=[], multi_snps=[] )

        self.assertEqual(snptk.app.map_using_coord_logic(self.bim_entries, snps, dbsnp, keep_multi, keep_unmapped_rsids), expected)

    def test_keep_multi_no_update(self):
        snps = ['rs123']
        dbsnp = {'6:123' :  ['rs123', 'rs456']}
        keep_multi = True
        keep_unmapped_rsids = False

        expected = UpdateLogic_map_using_coord_Output(
                snps_del=[], snps_up=[], multi_snps=[('6:123', ['rs123', 'rs456'])] )

        self.assertEqual(snptk.app.map_using_coord_logic(self.bim_entries, snps, dbsnp, keep_multi, keep_unmapped_rsids), expected)

    def test_keep_multi_update(self):
        snps = ['rs123']
        dbsnp = {'6:123' :  ['rs456', 'rs789']}
        keep_multi = True
        keep_unmapped_rsids = False

        expected = UpdateLogic_map_using_coord_Output(
                snps_del=[], snps_up=[('rs123', 'rs456')], multi_snps=[('6:123', ['rs456', 'rs789'])] )

        self.assertEqual(snptk.app.map_using_coord_logic(self.bim_entries, snps, dbsnp, keep_multi, keep_unmapped_rsids), expected)

    def test_keep_multi_no_update_snp_already_in_bim(self):
        snps = ['rs123', 'rs456']
        dbsnp = {'6:123' :  ['rs456', 'rs789']}
        keep_multi = True
        keep_unmapped_rsids = False

        expected = UpdateLogic_map_using_coord_Output(
                snps_del=[], snps_up=[], multi_snps=[('6:123', ['rs456', 'rs789'])] )

        self.assertEqual(snptk.app.map_using_coord_logic(self.bim_entries, snps, dbsnp, keep_multi, keep_unmapped_rsids), expected)

    def test_no_rs_keep_unmapped(self):
        snps = ['rs123']
        dbsnp = {}
        keep_multi = False
        keep_unmapped_rsids = True

        expected = UpdateLogic_map_using_coord_Output(
                snps_del=['123'], snps_up=[], multi_snps=[] )

        self.assertEqual(snptk.app.map_using_coord_logic(self.bim_entries_no_rs, snps, dbsnp, keep_multi, keep_unmapped_rsids), expected)

    def test_skip_rs_ids(self):
        snps = ['rs123']
        dbsnp = {'6:123' :  ['rs456']}
        keep_multi = False
        keep_unmapped_rsids = False
        skip_rs_ids = True

        expected = UpdateLogic_map_using_coord_Output(
                snps_del=[], snps_up=[], multi_snps=[] )

        self.assertEqual(snptk.app.map_using_coord_logic(self.bim_entries, snps, dbsnp, keep_multi, keep_unmapped_rsids, skip_rs_ids), expected)

