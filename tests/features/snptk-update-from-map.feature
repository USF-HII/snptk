Feature: SnpTk Update From Map

   Scenario: Update From Map Using Coordinates
       Given bim,bed,fam from map
           | chromosome  | variant_id | position | coordinate |
           | 1           | rs123      | 0        | 1111       |
           | 2           | rs456      | 0        | 2222       |
       And updated_snps.txt with
           | rs123       | rs888  |
       And deleted_snps.txt with nothing

       When we run snptk update-from-map . test final

       Then final.bim should be
           |1            | rs888      | 0        | 1111       | C | A |
           |2            | rs456      | 0        | 2222       | C | A |


   Scenario: Update From Map Using RS Id
       Given bim,bed,fam from map
           | chromosome  | variant_id | position | coordinate |
           | 1           | rs123      | 0        | 1111       |
           | 2           | rs456      | 0        | 2222       |
       And updated_snps.txt with
           | rs123       | rs888  |
       And deleted_snps.txt with nothing
       And coord_update.txt with
           | rs888      | 9999   |
       And chr_update.txt with nothing

       When we run snptk update-from-map . test final

       Then final.bim should be
           |1            | rs888      | 0        | 9999       | C | A |
           |2            | rs456      | 0        | 2222       | C | A |

