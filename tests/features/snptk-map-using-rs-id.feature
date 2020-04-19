Feature: SnpTk Map Using RS Id

    Given a PLINK extended MAP file (.bim) (https://www.cog-genomics.org/plink/1.9/formats#bim)

    Read in:
    - test.bim
    - dbsnp.gz
    - rsmerge.gz

    Write out:
    - updated_snps.txt - Variant ids that should be updated (variant id, new variant id) (uses rsmerge)
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
        And rsmerge.gz with
            | old  | new  |
            | 9999 | 1111 |

        When we run snptk map-using-rs-id --rs-merge=rsmerge.gz --dbsnp=dbsnp.gz --output-prefix . test.bim

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
        And rsmerge.gz with
            | old  | new |
            | 123  | 456 |

        When we run snptk map-using-rs-id --rs-merge=rsmerge.gz --dbsnp=dbsnp.gz --output-prefix . test.bim

        Then updated_snps.txt should be
            | rs123 | rs456 |
        And deleted_snps.txt should be empty
        And coord_update.txt should be empty
        And chr_update.txt should be empty
