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

        When we run snptk map-using-coord --dbsnp=dbsnp.gz --output-prefix . test.bim

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

        When we run snptk map-using-coord --dbsnp=dbsnp.gz --output-prefix . test.bim

        Then updated_snps.txt should be
            | rs123 | rs456 |
        And deleted_snps.txt should be empty
