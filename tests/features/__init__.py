import gzip
import os
import subprocess
import sys
import shutil

from nose.tools import assert_equal

from aloe import before, step, world

TEST_DIR = "tmp/tests/features"

PLINK = "/shares/hii/sw/plink1.9/current/bin/plink"

def cmd(args):
    if os.environ.get("DEBUG"):
        print(f"> {args}", file=sys.stderr)

    cp = subprocess.run(args, shell=True, cwd=TEST_DIR, capture_output=True, text=True)

    if cp.returncode != 0:
        print(args)
        print(cp.stderr)
        assert False


def write_tsv(fname, rows):
    if fname.endswith(".gz"):
        with gzip.open(f"{TEST_DIR}/{fname}", "wt") as f:
            for row in rows:
                print("\t".join(row), file=f)
    else:
        with open(f"{TEST_DIR}/{fname}", "wt") as f:
            for row in rows:
                print("\t".join(row), file=f)


@before.each_example
def clear(*args):
    shutil.rmtree(f"{TEST_DIR}")
    os.makedirs(f"{TEST_DIR}")


@step(f"bim,bed,fam from map")
def bim_bed_fam_set_with(self):
    write_tsv("test.map", self.table[1:])
    write_tsv("test.ped", [
        ["fid1", "iid1", "pid1", "mid1", "1", "1"] + ["A", "C"] * len(self.table[1:]),
        ["fid1", "iid2", "pid1", "mid1", "1", "1"] + ["A", "C"] * len(self.table[1:])
    ])

    cmd(f"{PLINK} --make-bed --map test.map --ped test.ped --out test")


@step(r"we run snptk ([a-z-]+) (.*)")
def we_run_snptk(self, subcommand, args):
    cmd_string = os.path.join(os.getcwd(), "bin/snptk") + " " + subcommand

    if subcommand == "remove-duplicates":
        cmd_string += f" --plink {PLINK}"
        cmd_string += f" --bcftools '/shares/hii/sw/singularity/latest/bin/singularity exec --bind /shares:/shares --bind /hii/work:/hii/work /shares/hii/images/bioinfo/htslib/latest.simg bcftools'"

    if subcommand == "update-from-map":
        cmd_string += f" --plink {PLINK}"

    cmd_string += " " + args

    cmd(cmd_string)


@step(r" (.*) should be\s*(\w+)?")
def should_be(self, fname, description):
    if description == "empty":
        assert_equal(os.path.exists(f"{TEST_DIR}/{fname}"), True, msg=f"{fname} does not exist")
        assert_equal(os.path.getsize(f"{TEST_DIR}/{fname}"), 0, msg=f"{fname} not empty")
    else:
        lines = []
        with open(f"{TEST_DIR}/{fname}") as f:
            for line in f:
                lines.append(tuple(line.rstrip("\n").split("\t")))

        assert_equal(tuple(self.table), tuple(lines))


@step(r"(test.bim|dbsnp.gz|rsmerge.gz|include.gz) with")
def test_bim_with(self, fname):
    write_tsv(fname, self.table[1:])


@step(r"(\w+\.txt) with\s*(\w+)?")
def fname_txt_with(self, fname, description):
    if description == "nothing":
        os.mknod(os.path.join(TEST_DIR, fname))
    else:
        write_tsv(fname, self.table)
