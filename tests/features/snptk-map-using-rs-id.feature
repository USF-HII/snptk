# NOTE: In tests/features/__init__.py we add the option --dbsnp-offset=0 to the snptk
# map-using-rs-id and map-using-coord subcommands to make the tests more readable.
# In the actual SNPChrPosOnRef file (and refsnp-<chromosome>.json.bz2 files) the default
# (--dbsnp-offset=1) is correct.

Feature: SnpTk Map Using RS Id

    Given a PLINK extended MAP file (.bim) (https://www.cog-genomics.org/plink/1.9/formats#bim)

    Read in:
    - test.bim
    - dbsnp.gz
    - refsnp-merged.gz

    Write out:
    - updated_snps.txt - Variant ids that should be updated (variant id, new variant id) (uses refsnp-merged)
    - deleted_snps.txt - Variant ids that should be removed (variant id) (uses dbsnp)
    - coord_update.txt - Updated coordinates (variant id, coordinate) (uses dbsnp)
    - chr_update.txt - Updated chromosome (variant id, chromosome) (uses dbsnp)

    Scenario: Remove bim entry that does not exist in dbsnp
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | rs123      | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate |
            | 456        | 1          | 2222       |
        And refsnp-merged.gz with
            | old  | new  |
            | 9999 | 1111 |

        When we run snptk map-using-rs-id --refsnp-merged=refsnp-merged.gz --dbsnp=dbsnp.gz test.bim .

        Then updated_snps.txt should be empty
        And deleted_snps.txt should be
            |rs123|
        And coord_update.txt should be empty
        And chr_update.txt should be empty


    Scenario: Update bim entry that has a merged variant id
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | rs123      | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate |
            | 456        | 1          | 1111       |
        And refsnp-merged.gz with
            | old  | new |
            | 123  | 456 |

        When we run snptk map-using-rs-id --refsnp-merged=refsnp-merged.gz --dbsnp=dbsnp.gz test.bim .

        Then updated_snps.txt should be
            | rs123 | rs456 |
        And deleted_snps.txt should be empty
        And coord_update.txt should be empty
        And chr_update.txt should be empty


    Scenario: Update bim entry that has a merged variant id and update to the new coordinate
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | rs123      | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate |
            | 456        | 1          | 2222       |
        And refsnp-merged.gz with
            | old  | new |
            | 123  | 456 |

        When we run snptk map-using-rs-id --refsnp-merged=refsnp-merged.gz --dbsnp=dbsnp.gz test.bim .

        Then updated_snps.txt should be
            | rs123 | rs456 |
        And deleted_snps.txt should be empty
        And coord_update.txt should be
            | rs456  | 2222 |
        And chr_update.txt should be empty


    Scenario: Remove bim entry that have been merged that are already present in bim
        """
        Sometimes when we merge an old variant id to a newer variant id, the new variant id already existed somewhere
        else in the file. We need to keep track of this and remove the old entry, otherwise we will have duplicates.
        """
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | rs123      | 0        | 1111       | A        | C        |
            | 1           | rs456      | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate |
            | 123        | 1          | 1111       |
            | 456        | 1          | 1111       |
        And refsnp-merged.gz with
            | old  | new |
            | 123  | 456 |

        When we run snptk map-using-rs-id --refsnp-merged=refsnp-merged.gz --dbsnp=dbsnp.gz test.bim .

        Then updated_snps.txt should be empty
        And deleted_snps.txt should be
            | rs123 |
        And coord_update.txt should be empty
        And chr_update.txt should be empty


    Scenario: Remove bim entry that has been merged but the merged id is already present in the bim and update coordinate and chromosome
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | rs123      | 0        | 1111       | A        | C        |
            | 1           | rs456      | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate |
            | 123        | 1          | 1111       |
            | 456        | 2          | 2222       |
        And refsnp-merged.gz with
            | old  | new |
            | 123  | 456 |

        When we run snptk map-using-rs-id --refsnp-merged=refsnp-merged.gz --dbsnp=dbsnp.gz test.bim .

        Then updated_snps.txt should be empty
        And deleted_snps.txt should be
            | rs123 |
        And coord_update.txt should be
            | rs456 | 2222 |
        And chr_update.txt should be
            | rs456 | 2 |


    Scenario: Skip snps that are present in include.gz and that are not in dbsnp
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | rs123      | 0        | 1111       | A        | C        |
            | 1           | rs456      | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate |
            | 456        | 1          | 1111       |
        And refsnp-merged.gz with
            | old  | new |
            | 111  | 222 |
        And include.gz with
            | variant_id |
            | 123        |

        When we run snptk map-using-rs-id --refsnp-merged=refsnp-merged.gz --dbsnp=dbsnp.gz --include-file=include.gz test.bim .

        Then updated_snps.txt should be empty
        And deleted_snps.txt should be empty
        And coord_update.txt should be empty
        And chr_update.txt should be empty


    Scenario: Skip snps that have been merged and are present in include.gz and that are not in dbsnp
        Given test.bim with
            | chromosome  | variant_id | position | coordinate | allele_1 | allele_2 |
            | 1           | rs456      | 0        | 1111       | A        | C        |
        And dbsnp.gz with
            | variant_id | chromosome | coordinate |
            | 123        | 1          | 1111       |
        And refsnp-merged.gz with
            | old  | new |
            | 456  | 789 |
        And include.gz with
            | variant_id  |
            | 789 |

        When we run snptk map-using-rs-id --refsnp-merged=refsnp-merged.gz --dbsnp=dbsnp.gz --include-file=include.gz test.bim .

        Then updated_snps.txt should be
            | rs456  | rs789 |
        And deleted_snps.txt should be empty
        And coord_update.txt should be empty
        And chr_update.txt should be empty
