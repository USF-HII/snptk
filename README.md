# snptk

Helps analyze,translate SNP entries from NCBI dbSNP and others.

## Usage

    snptk <sub_command> [options...]

### snpid-from-coord

Updates the SNP Id column in a Plink [BIM](https://www.cog-genomics.org/plink2/formats#bim) formatted file
and outputs to `STDOUT`.

     snptk snpid-from-coord --dbsnp=tmp/data/grch38p7/dbsnp.d/ tests/data/example.bim

## Concurrency

Since the reference files `snptk` deals with are rather large in number of records we have included a split utility to read the original file and split it into chunks within a directory.

If the input file is a directory as opposed to a file, the utility will use `concurrent.futures.ProcessPoolExecutor()` to parse all of the files in the directory to increase speed. It will use as many processes as there are files in the directory - currently 32 is a good guideline (the most expected on any node).

The recommended directory structure for a split file is `<file_path>.d/01`, `<file_path>.d/02`, etc.

For example:

    snptk-split \
      /shares/hii/bioinfo/ref/ncbi/human_9606_b151_GRCh38p7/b151_SNPChrPosOnRef_108.bcp.gz \
      tmp/data/grch38p7/dbsnp.d/ \
      32
