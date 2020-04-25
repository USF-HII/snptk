# snptk

Update [Plink](https://www.cog-genomics.org/plink2)
[BIM](https://www.cog-genomics.org/plink/1.9/formats#bim) files and
BIM,
[BED](https://www.cog-genomics.org/plink/1.9/formats#bed),
[FAM](https://www.cog-genomics.org/plink/1.9/formats#fam)
filesets utilizing [NCBI dbSNP](https://www.ncbi.nlm.nih.gov/snp/) data files.

## Concepts

- NCBI dbSNP SNPChrPosOnRef file
- NCBI dbSNP RsMergeArch file
- Reference SNP Id (RS Id)
- Variant ID


## Usage and Subcommands

```
snptk <subcommand> [--help] [--version] [options...]

Subcommands:

map-using-coord      Generate Plink update files by chromosome/coordinate of BIM entry
map-using-rs-id      Generate Plink update files by Reference SNP (RS) Id of BIM entry
remove-duplicates    Remove duplicate snps from Plink BIM,BED,FAM fileset
update-from-map      Update Plink BIM,BED,FAM fileset using output from map-using-coord or map-using-rs-id
```

### map-using-coord

Generate Plink update files by chromosome/coordinate of BIM entry.

```
Usage: snptk map-using-coord [--help] [--bim-offset BIM_OFFSET] [--keep-multi] [--keep-unmapped-rs-ids] [--skip-rs-ids]
                             --dbsnp DBSNP
                             input_bim output_map_dir

positional arguments:
input_bim
output_map_dir

optional arguments:
--help, -h               Show this help message and exit
--bim-offset BIM_OFFSET  Add BIM_OFFSET to each BIM entry coordinate
--keep-multi             If coordinate maps to multiple RS Ids, write out Chrom Coord RSId,RSId,... into multi.txt
--keep-unmapped-rs-ids   If entry starts with rs and is not in dbsnp, keep it anyways
--skip-rs-ids            Do not update/delete any entry which starts with rs
--dbsnp DBSNP, -d DBSNP  NCBI dbSNP SNPChrPosOnRef file or directory with split-files
```

The subcommand will will generate 2 Plink update files:
- `<output_map_dir>/deleted_snps.txt`
- `<output_map_dir>/updated_snps.txt`

The file `deleted_snps.txt` contains variant ids to remove that did not have a matching chromosome/coordinate
in the NCBI dbSNP SNPChrPosOnRef file.

The file `updated_snps.txt` is a tab-separated file containing `old variant id`, `new rs id` pairs
based on matching chromosome/coordinate in the NCBI dbSNP SNPChrPosOnRef file.

These files are used by the `plink --make-bed` command to create an updated copy of a `BIM,BED,FAM` fileset.

The operations are expected to be run in order, with `deleted_snps.txt` applied first followed by `updated_snps.txt`.

To update `old.bim, old.bed, old.fam` to `new.bim, new.bed, new.fam` using `deleted_snps.txt`:
```
plink --make-bed --exclude deleted_snps.txt --bfile old --out new
```

To update `old.bim, old.bed, old.fam` to `new.bim, new.bed, new.fam` using `updated_snps.txt`:
```
plink --make-bed --update-name updated_snps.txt --bfile old --out new
```

There are several options which modify behavior of the `map-using-coord` subcommand:

Normally, if the chromosome/coordinate map to more than one entry in the NCBI dbSNP SNPChrPosOnRef file, the
variant id is added to `deleted_snps.txt`. If `--keep-multi` is specified, we use the first entry
that maps and write out all matching entries to the file `multi.txt` in the format `chromosome:position<tab>rsid,rsid[,rsid...]`.

If `--keep-unmapped-rs-ids` is specified, if the variant id starts with the string `rs`, do not add it to `deleted_snps.txt` if
its chromosome/position does not map to an entry in SNPChrPosOnRef.

If `--skip-rs-ids` is specified, do not add any variant id that starts with the string `rs` to either `deleted_snps.txt` or `updated_snps.txt'.
