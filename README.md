# SNPTk - SNP Toolkit

The SNP Toolkit (SNPTk) analyzes and updates [Plink](https://www.cog-genomics.org/plink2)
[GWAS](https://en.wikipedia.org/wiki/Genome-wide_association_study) files.

## Table of Contents

- [Usage](#Usage)
  - [map-using-coord](#map-using-coord)
  - [map-using-rs-id](#map-using-rs-id)
  - [remove-duplicates](#remove-duplicates)
  - [upate-from-map](#update-from-map)
- [Plink Update Files](#plink-update-files)
- [RefSNP Merged](#refsnp-merged)
- [Concepts](#Concepts)
  - [dbSNP](#dbSNP)
  - [refSNP](#RefSNP)
  - [SNPChrPosOnRef](#SNPChrPosOnRef)

## Usage

```
snptk <subcommand> [--help] [--version] [options...]

Subcommands:

map-using-coord      Generate Plink update files by chromosome/coordinate of BIM entry
map-using-rs-id      Generate Plink update files by Reference SNP (RS) ID of BIM entry
remove-duplicates    Remove duplicate snps from Plink BIM,BED,FAM fileset
update-from-map      Update Plink BIM,BED,FAM fileset using output from map-using-coord or map-using-rs-id
```

### Subcommands

#### map-using-coord

Generate Plink update files by chromosome/coordinate of BIM entry.

```
usage: snptk map-using-coord
         [--help]
         [--bim-offset OFFSET]
         [--dbsnp-offset OFFSET]
         [--keep-multi]
         [--keep-unmapped-rs-ids]
         [--skip-rs-ids]
         --dbsnp DBSNP
         input_bim
         output_map_dir

positional arguments:
input_bim
output_map_dir

optional arguments:
--help, -h               Show this help message and exit
--bim-offset OFFSET      Add OFFSET to each BIM entry coordinate
--dbsnp-offset OFFSET    Add OFFSET to each DBSNP coordinate
--keep-multi             If coordinate maps to multiple RS IDs, write out Chrom Coord RSID,RSID,... into multi.txt
--keep-unmapped-rs-ids   If entry starts with rs and is not in dbsnp, keep it anyways
--skip-rs-ids            Do not update/delete any entry which starts with rs
--dbsnp DBSNP, -d DBSNP  NCBI dbSNP SNPChrPosOnRef file or directory with split-files
```

The subcommand will generate update files under `output_map_dir` (which is created if it does not exist):
- `deleted_snps.txt` - contains entries in the form `<variant_id>`
- `updated_snps.txt` - contains entries in the form `<variant_id><TAB><new_rs_id>`

See: [Plink Update Files](#plink-update-files) for how to apply these using Plink.

There are several options which modify behavior of the `map-using-coord` subcommand.

Normally, if the chromosome/coordinate map to more than one entry in the NCBI dbSNP SNPChrPosOnRef file, the
variant id is added to `deleted_snps.txt`. If `--keep-multi` is specified, we use the first entry
that maps and write out all matching entries to the file `multi.txt` in the format `chromosome:position<tab>rsid,rsid[,rsid...]`.

If `--keep-unmapped-rs-ids` is specified and the variant id starts with the string `rs`, do not add it to `deleted_snps.txt` if its chromosome/position does not map to an entry in SNPChrPosOnRef.

If `--skip-rs-ids` is specified, do not add any variant id that starts with the string `rs` to either `deleted_snps.txt` or `updated_snps.txt`.

#### map-using-rs-id

```
usage: snptk map-using-rs-id
         [--help]
         [--bim-offset OFFSET]
         [--dbsnp-offset OFFSET]
         [--include-file INCLUDE_FILE]
         --dbsnp DBSNP
         --refsnp-merged FILE|DIR
         input_bim
         output_map_dir

positional arguments:
  input_bim
  output_map_dir

optional arguments:
  --help, -h                            Show this help message and exit
  --bim-offset OFFSET                   Add OFFSET to each BIM entry coordinate
  --dbsnp-offset OFFSET                 Add OFFSET to each DBSNP coordinate
  --include-file INCLUDE_FILE           Do not remove variant ids listed in this file
  --dbsnp DBSNP, -d DBSNP               NCBI dbSNP SNPChrPosOnRef file or directory with split-files
  --refsnp-merged FILE|DIR, -r FILE|DIR Tab-separated gzipped file (or directory w/ gzipped split-files) generated from NCBI refsnp-
                                        merged.json.bz2
```

The subcommand will generate update files under `output_map_dir` (which is created if it does not exist):
- `deleted_snps.txt` - contains entries in the form `<variant_id>`
- `updated_snps.txt` - contains entries in the form `<variant_id><TAB><new_rs_id>`
- `coord_update.txt` - contains entries in the form `<variant_id><TAB><new_coordinate>`
- `chr_update.txt` - contains entries in thhe form `<variant_id><TAB><new_chromosome>`

See: [Plink Update Files](#plink-update-files) for how to apply these using Plink.

Instructions for generating the `--refsnp-merged` tab-separated gzipped file (or directory with gzipped split-files) is explained in the [refsnp-merged](#refsnp-merged) section below.

Normally variant ids that do not map to [SNPChrPosOnRef](#SNPChrPosOnRef) are added to the list of variant ids to be deleted.
If the option `--include-file INCLUDE_FILE` is specified, variant ids in `INCLUDE_FILE` that are not
in SNPChrPosOnRef (before or after merging) are not added to the list to be deleted.

#### remove-duplicates

```
usage: snptk remove-duplicates
         [--help]
         [--plink PLINK]
         [--bcftools BCFTOOLS]
         [--dry-run]
         input_prefix
         output_prefix

positional arguments:
  input_prefix         Input path prefix shared by Plink BIM,BED,FAM files
  output_prefix        Output path prefix to write out Plink BIM,BED,FAM files

optional arguments:
  --help, -h           Show this help message and exit
  --plink PLINK        Path to plink command
  --bcftools BCFTOOLS  Path to bcftools command
  --dry-run, -n        Print the commands that would be executed, but do not execute them
```

#### update-from-map

```
usage: snptk update-from-map
         [--help]
         [--dry-run]
         [--plink PLINK]
         map_dir
         input_prefix
         output_prefix

positional arguments:
  map_dir        Directory containing update files from map-using-coord/map-using-rs-id
  input_prefix   Input path prefix shared by Plink BIM,BED,FAM files
  output_prefix  Output path prefix to write out Plink BIM,BED,FAM files

optional arguments:
  --help, -h     Show this help message and exit
  --dry-run, -n  Print the commands that would be executed, but do not execute them
  --plink PLINK  Path to plink command
```

## Plink Update Files

The subcommands `map-using-coord` and `map-using-rs-id` generate a set of update files which are used by Plink to
change a `BIM,BED,BAM` fileset.

The subcommand `map-using-coord` generates `deleted_snps.txt` and `updated_snps.txt`.

The subcommand `map-using-rs-id` generates `deleted_snps.txt`, `updated_snps.txt`, `coord_update.txt`, and `chr_update.txt`.

These files are expected to be applied in the order listed above. This is because in some circumstances an entry may be
deleted or updated first, only for that entry or a later entry to be updated again in a following step.

The subcommand `update-using-map` will read a directory (`--map-dir`) with the update files and run plink commands
on a `BIM,BED,BAM` fileset. You can also run the subcommand with the `--dry-run` option and use the commands it
would run in your own script.

Each update file is intended to be used by the `plink --make-bed` function.

Here are example commands to update `old.bim, old.bed, old.fam` to `new.bim, new.bed, new.fam` for `map-using-coord`:
```
plink --make-bed --exclude deleted_snps.txt --bfile old --out new.deleted
plink --make-bed --update-name updated_snps.txt --bfile new.deleted --out new
```

To update `old.bim, old.bed, old.fam` to `new.bim, new.bed, new.fam` using `updated_snps.txt`:
```
plink --make-bed --exclude deleted_snps.txt --bfile old --out new.deleted
plink --make-bed --update-name updated_snps.txt --bfile new.deleted --out new.updated_snps
plink --make-bed --update-name coord_update.txt --bfile new.updated_snps --out new.coord_update
plink --make-bed --update-name chr_update.txt --bfile new.coord_update --out new
```

## RefSNP Merged

The `map-using-rs-id` subcommand option `--refsnp-merged` expects a gzipped tab-separated file or directory containing
split-files generated from the NCBI SNP JSON file <https://ftp.ncbi.nih.gov/snp/latest_release/JSON/refsnp-merged.json.bz2>.

**Note** - If you wish to use a build-specific version of `refsnp-merged.json.bz2`, for example Build 153, the JSON
file to download would be <https://ftp.ncbi.nih.gov/snp/archive/b153/JSON/refsnp-merged.json.bz2>.

This file contains Reference SNP IDs that have been merged, which means that on newer genome assemblies,
the Reference SNP ID is now located at the same coordinate as a previous SNP.
We "merge" or update the newer Reference SNP ID to the older Reference SNP ID.

For example, imagine `rs456` originally maps to `chr1:5555` and `rs123` maps to `chr1:2222`. On a newer
genome assembly, it is discovered `rs456` actually maps to `chr1:2222`. There will therefore
be an entry specifying `rs456<tab>rs123` indicating we should change `rs456` to `rs123` since it maps
to the same location.

The information contained in the new `refsnp-merged.json.bz2` file was previously maintained in the dbSNP [RsMergeArch](https://www.ncbi.nlm.nih.gov/projects/SNP/snp_db_table_description.cgi?t=RsMergeArch) file.

### Generate Single File

Steps to generate a single gzipped tab-separated file using the SNPTk Utility `bin/extract-refsnp-merged.py`

```
mkdir tmp
curl -s https://ftp.ncbi.nih.gov/snp/latest_release/JSON/refsnp-merged.json.bz2 > tmp/refsnp-merged.json.bz2
python3 bin/extract-refsnp-merged.py tmp/refsnp-merged.json.bz2 tmp/refsnp-merged.gz
```

### Generate Directory with Split-Files

If you are running SNPTk on a multi-processor system, you can createda directory of split files and SNPTk will
load these in parallel to speed execution time.

Steps to generate a directory of 32 split gzipped tab-separated files using the SNPTk Utility `bin/extract-refsnp-merged.py`

```
mkdir tmp
curl -s https://ftp.ncbi.nih.gov/snp/latest_release/JSON/refsnp-merged.json.bz2 > tmp/refsnp-merged.json.bz2
python3 bin/extract-refsnp-merged.py --split=32 tmp/refsnp-merged.json.bz2 tmp/refsnp-merged.d/
```

(This will create `tmp/refsnp-merged.d/01.gz`, `tmp/refsnp-merged.d/02.gz`, ... `tmp/refsnp-merged.d/32.gz`)

## Concepts

### dbSNP

The [NCBI](https://www.ncbi.nlm.nih.gov/snp/) [dbSNP](https://www.ncbi.nlm.nih.gov/snp/) is a public-domain archive or a broad collection of simple genetic polymorphisms.

### RefSNP

A RefSNP (Reference SNP) is a number prefixed with `rs` (e.g. `rs123`) which is "a locus accession for a variant type assigned by dbSNP. The RefSNP catalog is a non-redundant collection of submitted variants which were clustered, integrated and annotated. RefSNP number is the stable accession regardless of the differences in genomic assemblies."

### SNPChrPosOnRef

SNPChrPosOnRef is a dump of the NCBI dbSNP. This was a flat file up to Build 151 (e.g. `b151_SNPChrPosOnRef_108.bcp.gz`)
with the following tab-separated format (from: <https://www.ncbi.nlm.nih.gov/SNP/snp_db_table_description.cgi?t=SNPChrPosOnRef>):
- `snp_id` - RefSNP (e.g. `123`). Note the `rs` is not present on this database dump
- `chr` -  Chromosome (e.g. `X`)
- `pos` - The 0 based chromosome position of uniquely mapped snp
- `orien` - SNP to chromosome orientation. 0 - same orientation (or same strand), 1 - opposite strand
- `neighbor_snp_list` - Internal use
- `isPAR` - The SNP is in Pseudoautosomal Region (PAR) region when isPAR value is `y`

**Note** - As of Build 152 the information once held in SNPChrPosOnRef is now contained in a much richer JSON format (See: <https://ftp.ncbi.nih.gov/snp/latest_release/JSON/>) and we plan to incorporate this in the near future.
