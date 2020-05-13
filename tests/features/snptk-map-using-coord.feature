# NOTE: In tests/features/__init__.py we add the option --dbsnp-offset=0 to the snptk
# map-using-rs-id and map-using-coord subcommands to make the tests more readable.
# In the actual SNPChrPosOnRef file (and refsnp-<chromosome>.json.bz2 files) the default
# (--dbsnp-offset=1) is correct.

Feature: SnpTk Map Using Coord

    Given a PLINK extended MAP file (.bim) (https://www.cog-genomics.org/plink/1.9/formats#bim), read in the chromosome
    and base-pair coordinates, compare with dbsnp and generate:
    - updated_snps.txt - variant ids that should be updated (variant id, new variant id) using dbsnp
    - deleted_snps.txt - file with variant ids that should be removed (variant id) using dbsnp

    Scenario: Remove bim entry that has wrong coordinate in dbsnp
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | rs123      | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate |
            | 123        | 3          | 4444       |

        When we run snptk map-using-coord --dbsnp=dbsnp.gz test.bim .

        Then deleted_snps.txt should be
            |rs123|
        And updated_snps.txt should be empty


    Scenario: Update bim entry whose variant id has change
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | rs123      | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate | orientation |
            | 456        | 1          | 1111       | 0           |

        When we run snptk map-using-coord --dbsnp=dbsnp.gz test.bim .

        Then updated_snps.txt should be
            | rs123 | rs456 |
        And deleted_snps.txt should be empty


    Scenario: Remove bim entry not found in dbsnp
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | rs123      | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate | orientation |
            | 456        | 1          | 2222       | 0           |

        When we run snptk map-using-coord --dbsnp=dbsnp.gz test.bim .

        Then updated_snps.txt should be empty
        And deleted_snps.txt should be
            | rs123 |


    Scenario: Keep bim entry not found in dbsnp when --keep-unmapped-rs-ids
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | rs123      | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate | orientation |
            | 456        | 1          | 2222       | 0           |

        When we run snptk map-using-coord --dbsnp=dbsnp.gz --keep-unmapped-rs-ids test.bim .

        Then updated_snps.txt should be empty
        And deleted_snps.txt should be empty


    Scenario: Remove bim entry that has mutiple chromosome and coornidate mappings
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | rs123      | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate | orientation |
            | 123        | 1          | 1111       | 0           |
            | 456        | 1          | 1111       | 0           |

        When we run snptk map-using-coord --dbsnp=dbsnp.gz test.bim .

        Then updated_snps.txt should be empty
        And deleted_snps.txt should be
            | rs123 |


    Scenario: Keep bim entry that has mutiple chromosome and coornidate mappings when --keep-multi
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | rs123      | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate | orientation |
            | 123        | 1          | 1111       | 0           |
            | 456        | 1          | 1111       | 0           |

        When we run snptk map-using-coord --dbsnp=dbsnp.gz --keep-multi test.bim .

        Then updated_snps.txt should be empty
        And deleted_snps.txt should be empty


    Scenario: Update bim entry that has mutiple chromosome and coornidate mappings when --keep-multi
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | rs123      | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate | orientation |
            | 456        | 1          | 1111       | 0           |
            | 789        | 1          | 1111       | 0           |

        When we run snptk map-using-coord --dbsnp=dbsnp.gz --keep-multi test.bim .

        Then updated_snps.txt should be
            | rs123 | rs456 |
        And deleted_snps.txt should be empty


    Scenario: No change in bim entry that has mutiple chromosome and coornidate mappings when --keep-multi but already present in bim
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | rs123      | 0        | 1111       | A        | C        |
            | 1           | rs456      | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate | orientation |
            | 456        | 1          | 1111       | 0           |
            | 789        | 1          | 1111       | 0           |

        When we run snptk map-using-coord --dbsnp=dbsnp.gz --keep-multi test.bim .

        Then updated_snps.txt should be empty
        And deleted_snps.txt should be empty


    Scenario: Remove bim entry that does not start with 'rs' and not found in dbsnp
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | 123        | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate | orientation |
            | 456        | 1          | 2222       | 0           |
            | 789        | 1          | 3333       | 0           |

        When we run snptk map-using-coord --dbsnp=dbsnp.gz test.bim .

        Then updated_snps.txt should be empty
        And deleted_snps.txt should be
            | 123 |


    Scenario: No update to bim entry when --skip-rs-ids
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | rs123        | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate | orientation |
            | 123        | 1          | 2222       | 0           |

        When we run snptk map-using-coord --dbsnp=dbsnp.gz --skip-rs-ids test.bim .

        Then updated_snps.txt should be empty
        And deleted_snps.txt should be empty
