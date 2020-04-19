Feature: SnpTk Remove Duplicates

   Scenario: Remove duplicate entry
       Given bim,bed,fam from map
           | chromosome  | variant_id | position | coordinate |
           | 3           | rs123      | 0        | 1111       |
           | 3           | rs123      | 0        | 1111       |
       When we run snptk remove-duplicates --plink-prefix test --output-prefix .

       Then test_no_dups.bim should be
           |3            | rs123      | 0        | 1111       | C | A |
